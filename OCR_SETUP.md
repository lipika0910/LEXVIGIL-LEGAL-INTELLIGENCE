# Local OCR and evidence viewer

The local development install uses UB Mannheim Tesseract 5.4.0.20240606, installed with Windows Package Manager from its checksum-verified package. English, Tamil and Hindi language data comes from the official `tesseract-ocr/tessdata_fast` GitHub repository, tag `4.1.0`.

Runtime: `C:\Program Files\Tesseract-OCR\tesseract.exe`. Language data: `.runtime/tessdata`, ignored by Git. Configure `TESSERACT_CMD` and `TESSDATA_PREFIX` for other installations. The latter points directly to the folder containing the `.traineddata` files.

Model SHA-256 hashes:

- eng: `7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2`
- tam: `d02fbec24be4b07e32e80d0ccfc3b6b67a3c5d61c9d0a7c8532677990912c6ec`
- hin: `4c73ffc59d497c186b19d1e90f5d721d678ea6b2e277b719bee4e2af12271825`

## Behavior and limits

OCR is an explicit per-upload option. It runs locally for scanned/nearly empty PDF pages only. Existing text layers are preserved; images embedded alongside readable text are not separately recognized. Blank pages remain blank. At most 20 scanned pages per upload, a 30-second OCR subprocess timeout per page, and a 3000-pixel maximum rendered page dimension. The existing upload/page/text limits also apply. Any failed page fails the job instead of silently publishing a partial report.

Raster input and recognized text pass through process pipes. No temporary OCR image/text files are created by the adapter. Original storage still requires separate consent. OCR text is stored in the report snapshot and follows report retention, not the original's 48-hour clock.

The evidence viewer displays exact extracted-text spans, counting Unicode code points consistently with the backend. PDF image previews require a valid owner session and an unexpired original. Highlights are in extracted text, not pixel-aligned overlays. PDF preview pages are passive PNG images with a 1600-pixel maximum dimension; they do not execute PDF scripts or links. Deleting originals removes subsequent preview access but cannot erase already downloaded/browser-displayed copies.

## Verification and release gates

Tests include native-PDF preview, access isolation/expiry, source navigation, multiple spans, a non-BMP Unicode prefix, real synthetic English/Tamil/Hindi OCR, and OCR timeout handling. These are integration checks, not a legal-language accuracy benchmark. Complex layouts, poor scans, handwriting, mixed text/image PDFs, calibration and legal reasoning in Tamil/Hindi still require evaluation.

Production original storage remains disabled. Before launch, configure private encrypted storage, backup retention, isolated document-rendering/OCR workers, durable jobs, deployment packaging/licensing review and capacity limits. The current single-process development architecture is not a production workload guarantee.
