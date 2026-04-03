import { useMemo, useState } from 'react'
import { FileText, LoaderCircle, UploadCloud } from 'lucide-react'

const requiredFiles = [
  {
    id: 'questionPaper',
    label: 'Question Paper',
    helper: 'Upload the exam paper to extract prompts and marks.',
  },
  {
    id: 'answerKey',
    label: 'Answer Key',
    helper: 'Provide the ideal answers for rubric-based comparison.',
  },
  {
    id: 'studentAnswers',
    label: 'Student Answers',
    helper: 'Drop the combined student response PDF for clustering.',
  },
]

function UploadCard({ file, fileConfig, isDragging, onDrop, onSelect }) {
  return (
    <label
      className={`group relative flex min-h-44 cursor-pointer flex-col overflow-hidden rounded-[26px] border p-5 transition ${
        isDragging
          ? 'border-cyan-300 bg-cyan-300/10 shadow-[0_0_0_1px_rgba(103,232,249,0.35)]'
          : 'border-white/10 bg-slate-950/55 hover:border-cyan-200/30 hover:bg-slate-950/75'
      }`}
      htmlFor={fileConfig.id}
      onDragLeave={() => onDrop(fileConfig.id, null, false)}
      onDragOver={(event) => {
        event.preventDefault()
        onDrop(fileConfig.id, null, true)
      }}
      onDrop={(event) => {
        event.preventDefault()
        const droppedFile = event.dataTransfer.files?.[0] ?? null
        onDrop(fileConfig.id, droppedFile, false)
      }}
    >
      <div className="absolute inset-0 soft-grid opacity-40" />
      <div className="relative z-10 flex h-full flex-col">
        <div className="flex items-center justify-between">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/8 text-cyan-300 ring-1 ring-inset ring-white/10">
            <UploadCloud size={20} />
          </div>
          <span className="rounded-full border border-white/10 px-3 py-1 text-xs font-medium text-slate-300">
            PDF only
          </span>
        </div>

        <div className="mt-7 space-y-2">
          <h2 className="text-[1.9rem] font-semibold tracking-tight text-white">
            {fileConfig.label}
          </h2>
          <p className="max-w-sm text-sm leading-6 text-slate-300">
            {fileConfig.helper}
          </p>
        </div>

        <div className="mt-5 rounded-2xl border border-dashed border-white/10 bg-white/5 p-4">
          {file ? (
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-emerald-400/15 p-2 text-emerald-300">
                <FileText size={18} />
              </div>
              <div>
                <p className="text-sm font-semibold text-white">{file.name}</p>
                <p className="text-xs text-slate-400">
                  {(file.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              </div>
            </div>
          ) : (
            <>
              <p className="text-sm font-medium text-slate-200">
                Drag and drop your PDF here
              </p>
              <p className="mt-1 text-xs text-slate-400">
                Or click to browse from your device
              </p>
            </>
          )}
        </div>
      </div>

      <input
        accept="application/pdf"
        className="hidden"
        id={fileConfig.id}
        onChange={(event) => onSelect(fileConfig.id, event.target.files?.[0] ?? null)}
        type="file"
      />
    </label>
  )
}

function UploadPage({ isProcessing, onProcess }) {
  const [files, setFiles] = useState({
    answerKey: null,
    questionPaper: null,
    studentAnswers: null,
  })
  const [dragTarget, setDragTarget] = useState(null)

  const isReady = useMemo(
    () => requiredFiles.every((file) => files[file.id]),
    [files],
  )

  const handleFileUpdate = (id, nextFile) => {
    if (nextFile && nextFile.type && nextFile.type !== 'application/pdf') {
      return
    }

    setFiles((current) => ({
      ...current,
      [id]: nextFile,
    }))
  }

  const handleDropState = (id, nextFile, isDragging) => {
    setDragTarget(isDragging ? id : null)

    if (nextFile) {
      handleFileUpdate(id, nextFile)
    }
  }

  return (
    <main className="min-h-screen bg-[#efe8df] px-4 py-4 text-stone-900 sm:px-6 lg:px-8">
      <div className="mx-auto grid max-w-7xl gap-5 lg:grid-cols-[280px_minmax(0,1fr)]">
        <section className="relative overflow-hidden rounded-[32px] border border-stone-300 bg-[#1c2435] p-6 text-stone-50 shadow-[0_30px_80px_rgba(28,36,53,0.18)]">
          <div className="absolute -right-10 top-0 h-40 w-40 rounded-full bg-[#b6402c]/35 blur-3xl" />
          <div className="absolute left-0 top-0 h-48 w-48 rounded-full bg-[#f4b860]/10 blur-3xl" />
          <div className="relative flex h-full flex-col justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-[#f4b860]">
              Automated Assessment
            </p>
            <h1 className="mt-4 max-w-[12rem] text-4xl font-semibold leading-none tracking-tight text-white sm:text-5xl">
              Upload exam files.
            </h1>
            <p className="mt-4 max-w-sm text-sm leading-6 text-stone-300">
              Add the three PDFs and move straight into clustered grading review.
            </p>
          </div>

          <div className="mt-6 space-y-3">
            <div className="rounded-[24px] border border-white/10 bg-white/6 p-4">
              <p className="text-xs uppercase tracking-[0.3em] text-stone-400">
                Pipeline
              </p>
              <ul className="mt-3 space-y-2 text-sm text-stone-200">
                <li>1. Parse PDFs</li>
                <li>2. Cluster answers</li>
                <li>3. Review and score</li>
              </ul>
            </div>

            <button
              className="inline-flex w-full items-center justify-center gap-3 rounded-full bg-[#f4b860] px-5 py-3.5 text-sm font-semibold text-[#1c2435] transition hover:bg-[#f0c57d] disabled:cursor-not-allowed disabled:bg-stone-700 disabled:text-stone-300"
              disabled={!isReady || isProcessing}
              onClick={() => onProcess(files)}
              type="button"
            >
              {isProcessing ? (
                <>
                  <LoaderCircle className="animate-spin" size={18} />
                  Processing submissions...
                </>
              ) : (
                <>
                  <UploadCloud size={18} />
                  Process
                </>
              )}
            </button>
          </div>
          </div>
        </section>

        <section className="rounded-[32px] border border-stone-300 bg-[#f7f0e7] p-4 shadow-[0_30px_80px_rgba(91,67,49,0.08)] xl:p-5">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3 rounded-[24px] border border-stone-300 bg-white/55 px-4 py-3">
            <div>
              <p className="text-xs uppercase tracking-[0.32em] text-stone-500">
                Upload Set
              </p>
              <p className="mt-1 text-sm text-stone-700">
                Question paper, answer key, and student responses
              </p>
            </div>
            <div className="rounded-full bg-[#1c2435] px-4 py-2 text-xs font-semibold uppercase tracking-[0.24em] text-[#f4b860]">
              3 PDFs
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {requiredFiles.map((fileConfig) => (
              <UploadCard
                key={fileConfig.id}
                file={files[fileConfig.id]}
                fileConfig={fileConfig}
                isDragging={dragTarget === fileConfig.id}
                onDrop={handleDropState}
                onSelect={handleFileUpdate}
              />
            ))}
          </div>
        </section>
      </div>
    </main>
  )
}

export default UploadPage
