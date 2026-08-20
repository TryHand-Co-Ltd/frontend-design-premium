# File Upload Patterns

Read this when implementing file selection, multi-upload, drag-and-drop, validation, upload progress, or error recovery. This reference supplements the upload section in `data-entry-patterns.md` with component-level implementation guidance.

## Upload zone anatomy

A complete upload zone consists of:

1. **Drop target** — visible area with dashed border, hover/focus/drag-over states.
2. **Hidden file input** — `<input type="file">` for keyboard/click access.
3. **File list** — each file shows name, size, status, and a remove button.
4. **Validation feedback** — inline per-file errors for type, size, or count limits.
5. **Progress indicator** — during upload (determinate or indeterminate).

## Component structure

### Core state model

```tsx
const [files, setFiles] = useState<File[]>([]);
const [isDragOver, setIsDragOver] = useState(false);
const [uploading, setUploading] = useState(false);
const [errors, setErrors] = useState<Record<string, string>>({});
const fileInputRef = useRef<HTMLInputElement>(null);
```

### Drop zone with click fallback

```tsx
<div
  className={`flex cursor-pointer flex-col items-center justify-center rounded border-2 border-dashed p-8 transition-colors ${
    isDragOver ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-blue-400"
  }`}
  onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
  onDragLeave={() => setIsDragOver(false)}
  onDrop={(e) => { e.preventDefault(); setIsDragOver(false); handleFiles(e.dataTransfer.files); }}
  onClick={() => fileInputRef.current?.click()}
  role="button"
  tabIndex={0}
  onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") fileInputRef.current?.click(); }}
  aria-label="Upload files"
>
  <input
    ref={fileInputRef}
    type="file"
    accept={ACCEPTED_TYPES}
    multiple
    className="hidden"
    onChange={(e) => handleFiles(e.target.files)}
  />
  <UploadIcon />
  <p className="text-sm font-medium">Upload files</p>
  <p className="text-xs text-muted-foreground">PDF, DOCX, or TXT · Drag files or click to browse</p>
</div>
```

### File list with removal

```tsx
{files.length > 0 && (
  <div className="space-y-2">
    <p className="text-sm font-medium">
      {files.length} file{files.length !== 1 ? "s" : ""} selected
    </p>
    {files.map((file, i) => (
      <div key={`${file.name}-${i}`} className="flex items-center justify-between rounded border px-3 py-2.5 text-sm">
        <div className="flex min-w-0 items-center gap-2.5">
          <FileIcon className="size-4 shrink-0 text-muted-foreground" />
          <span className="truncate font-medium">{file.name}</span>
          <span className="shrink-0 text-xs tabular-nums text-muted-foreground">
            {(file.size / 1024).toFixed(0)} KB
          </span>
        </div>
        {errors[`${file.name}-${i}`] ? (
          <span className="text-xs text-destructive">{errors[`${file.name}-${i}`]}</span>
        ) : (
          <button
            type="button"
            className="text-xs text-muted-foreground underline hover:text-foreground"
            onClick={() => removeFile(i)}
          >
            Remove
          </button>
        )}
      </div>
    ))}
  </div>
)}
```

## Validation

### Client-side checks

Validate on selection, before upload:

```ts
const ACCEPTED_TYPES = ".pdf,.docx,.txt";
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB
const MAX_FILES = 20;

function validateFile(file: File): string | null {
  const ext = "." + file.name.split(".").pop()?.toLowerCase();
  if (!ACCEPTED_TYPES.includes(ext)) {
    return `${file.name}: unsupported file type. Accepted: ${ACCEPTED_TYPES}`;
  }
  if (file.size > MAX_FILE_SIZE) {
    return `${file.name}: file exceeds ${MAX_FILE_SIZE / 1024 / 1024} MB limit`;
  }
  if (file.size === 0) {
    return `${file.name}: file is empty`;
  }
  return null;
}

function handleFiles(fileList: FileList | null) {
  if (!fileList) return;

  const newFiles = Array.from(fileList);
  if (files.length + newFiles.length > MAX_FILES) {
    setGlobalError(`Maximum ${MAX_FILES} files allowed`);
    return;
  }

  const fileErrors: Record<string, string> = {};
  const validFiles: File[] = [];

  for (const file of [...files, ...newFiles]) {
    const err = validateFile(file);
    if (err) fileErrors[file.name + "-" + validFiles.length] = err;
    else validFiles.push(file);
  }

  setFiles(validFiles);
  setErrors((prev) => ({ ...prev, ...fileErrors }));
}
```

### Server-side validation

Never trust client validation alone. Verify on the server:

```ts
const formData = await request.formData();
const file = formData.get("file") as File;

if (!file || file.size === 0) {
  return Response.json({ error: "File is required" }, { status: 400 });
}
if (file.size > MAX_FILE_SIZE) {
  return Response.json({ error: "File too large" }, { status: 413 });
}
```

## Upload with progress

### Server-sent events for progress

```tsx
const uploadWithProgress = async (files: File[]) => {
  const formData = new FormData();
  files.forEach((f) => formData.append("files", f));

  const xhr = new XMLHttpRequest();
  xhr.upload.addEventListener("progress", (e) => {
    if (e.lengthComputable) {
      const pct = Math.round((e.loaded / e.total) * 100);
      setProgress(pct);
    }
  });

  return new Promise((resolve, reject) => {
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) resolve(JSON.parse(xhr.responseText));
      else reject(new Error(`Upload failed: ${xhr.status}`));
    };
    xhr.onerror = () => reject(new Error("Network error"));
    xhr.open("POST", "/api/upload");
    xhr.send(formData);
  });
};
```

### Abort controller for cancellation

```tsx
const abortRef = useRef<AbortController | null>(null);

const startUpload = async () => {
  abortRef.current = new AbortController();
  try {
    await fetch("/api/upload", {
      method: "POST",
      body: formData,
      signal: abortRef.current.signal,
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      // user cancelled — clean up partial upload
    } else {
      throw err;
    }
  }
};

const cancelUpload = () => {
  abortRef.current?.abort();
};
```

## States

| State | Visual | Behavior |
|-------|--------|----------|
| Idle | Dashed border, upload icon, "Click to browse or drag" | — |
| Drag over | Highlighted border, background tint | Prevent default on dragover/drop |
| Validating | File list shows pending state | Per-file validation |
| Uploading | Progress bar or indeterminate spinner | Per-file or batch progress |
| Success | Green checkmark, file listed as uploaded | Show preview or summary |
| Error (file) | Red text next to file, remove button | Keep other files intact |
| Error (network) | Banner at top, retry button | Global error, does not clear files |
| Cancelled | Greyed out, "Cancelled" label | Re-enable upload button |
| Too many files | Inline validation message | Block selection, show limit |

## Multi-file considerations

- Show total count and individual file details.
- Validate all files independently — one invalid file does not block valid ones.
- For batch upload, prefer showing per-file status rather than one global progress.
- Allow removing files from the queue without canceling the entire batch.
- For long-running uploads, support leave-and-return with session recovery.

## Drag-and-drop accessibility

- Drop zone is a real focusable element (`tabIndex={0}`, `role="button"`, `aria-label`).
- Keyboard users can activate the drop zone to open the file picker.
- Drag-over state must not be the only visual affordance — the zone is clickable.
- Announce file count and validation errors to screen readers.

## Do's and Don'ts

- **Do:** Show accepted types and size limits before selection.
- **Do:** Validate on both client and server.
- **Do:** Provide a visible file-picker button — drag is never the only method.
- **Do:** Allow removal of individual files from the queue.
- **Do:** Preserve valid files when one file fails validation.
- **Don't:** Trust file extension/MIME alone.
- **Don't:** Expose local file paths in the UI.
- **Don't:** Block upload for files that fail server-side only — show those errors inline.
- **Don't:** Clear the entire file list on a single error.
