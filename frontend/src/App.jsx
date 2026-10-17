import { useRef, useState } from "react";



import {

  Upload,

  ShieldCheck,

  FileSearch,

  Activity,

  ScanLine,

  AlertTriangle,

  CheckCircle2,

  Loader2,

  X,

  Image as ImageIcon,

  Maximize2,

  Lock,

  Clock3,

  FileText,

  Search,

  History,

  RefreshCw,

  Database,
  Printer,
  Bot,
  BrainCircuit,
  Cpu,

} from "lucide-react";



import "./App.css";





const API_BASE_URL = "http://127.0.0.1:8000";





function App() {



  const [page, setPage] = useState("scanner");



  const [selectedFile, setSelectedFile] = useState(null);



  const [preview, setPreview] = useState(null);



  const [result, setResult] = useState(null);



  const [loading, setLoading] = useState(false);



  const [error, setError] = useState("");



  const [dragActive, setDragActive] = useState(false);



  const [selectedEvidence, setSelectedEvidence] =

    useState(null);



  const [history, setHistory] = useState([]);



  const [historyLoading, setHistoryLoading] =

    useState(false);



  const [historyError, setHistoryError] =

    useState("");



  const [openingHistory, setOpeningHistory] =

    useState(false);



  const fileInputRef = useRef(null);





  // =======================================================

  // Fetch scan history

  // =======================================================



  const fetchHistory = async () => {



    setHistoryLoading(true);

    setHistoryError("");



    try {



      const response = await fetch(

        `${API_BASE_URL}/api/scan/history`

      );



      if (!response.ok) {

        throw new Error(

          `Unable to load history (${response.status})`

        );

      }



      const data = await response.json();



      setHistory(

        Array.isArray(data.records)

          ? data.records

          : []

      );



    } catch (requestError) {



      console.error(

        "History error:",

        requestError

      );



      setHistoryError(

        requestError.message ||

        "Unable to load scan history."

      );



    } finally {



      setHistoryLoading(false);



    }

  };





  // =======================================================

  // Open previous scan

  // =======================================================



  const openHistoryScan = async (scanId) => {



    setOpeningHistory(true);

    setHistoryError("");



    try {



      const response = await fetch(

        `${API_BASE_URL}/api/scan/history/${scanId}`

      );



      if (!response.ok) {



        throw new Error(

          `Unable to open scan (${response.status})`

        );



      }



      const data = await response.json();



      const record =

        data.record || data;



      setResult(record);



      setSelectedFile(null);



      setPreview(null);



      setPage("scanner");



    } catch (requestError) {



      console.error(

        "Open history error:",

        requestError

      );



      setHistoryError(

        requestError.message ||

        "Unable to open this scan."

      );



    } finally {



      setOpeningHistory(false);



    }

  };





  // =======================================================

  // Handle selected file

  // =======================================================



  const handleFile = (file) => {



    if (!file) {

      return;

    }



    if (!file.type.startsWith("image/")) {



      setError(

        "Please select a valid image file."

      );



      return;

    }



    setError("");



    setResult(null);



    setSelectedFile(file);



    const previewUrl =

      URL.createObjectURL(file);



    setPreview(previewUrl);

  };





  // =======================================================

  // File input

  // =======================================================



  const handleFileInput = (event) => {



    const file =

      event.target.files?.[0];



    if (file) {

      handleFile(file);

    }

  };





  // =======================================================

  // Drag and drop

  // =======================================================



  const handleDragOver = (event) => {



    event.preventDefault();



    setDragActive(true);

  };





  const handleDragLeave = (event) => {



    event.preventDefault();



    setDragActive(false);

  };





  const handleDrop = (event) => {



    event.preventDefault();



    setDragActive(false);



    const file =

      event.dataTransfer.files?.[0];



    if (file) {

      handleFile(file);

    }

  };





  // =======================================================

  // Clear current scan

  // =======================================================



  const clearFile = () => {



    setSelectedFile(null);



    setPreview(null);



    setResult(null);



    setError("");



    if (fileInputRef.current) {

      fileInputRef.current.value = "";

    }

  };





  // =======================================================

  // Analyze document

  // =======================================================



  const analyzeFile = async () => {



    if (!selectedFile) {



      setError(

        "Please select an image before analyzing."

      );



      return;

    }



    setLoading(true);



    setError("");



    setResult(null);



    try {



      const formData =

        new FormData();



      formData.append(

        "file",

        selectedFile

      );



      const response =

        await fetch(

          `${API_BASE_URL}/api/scan/full-scan`,

          {

            method: "POST",

            body: formData,

          }

        );



      if (!response.ok) {



        let message =

          `Analysis failed with status ${response.status}`;



        try {



          const errorData =

            await response.json();



          if (

            typeof errorData.detail ===

            "string"

          ) {



            message =

              errorData.detail;



          }



        } catch {

          // Keep default error.

        }



        throw new Error(message);

      }



      const data =

        await response.json();



      setResult(data);



    } catch (requestError) {



      console.error(

        "ScamScan error:",

        requestError

      );



      setError(

        requestError.message ||

        "Unable to connect to ScamScan backend."

      );



    } finally {



      setLoading(false);



    }

  };





  // =======================================================

  // Evidence URL

  // =======================================================



  const evidenceUrl = (path) => {



    if (!path) {

      return "";

    }



    if (

      path.startsWith("http://") ||

      path.startsWith("https://")

    ) {



      return path;



    }



    return `${API_BASE_URL}${path}`;

  };





  // =======================================================

  // Risk class

  // =======================================================



  const getRiskClass = (riskLevel = "") => {



    const normalized =

      riskLevel.toLowerCase();



    if (normalized.includes("high")) {

      return "risk-high";

    }



    if (

      normalized.includes("moderate") ||

      normalized.includes("medium")

    ) {



      return "risk-medium";

    }



    return "risk-low";

  };





  const riskScore =

    Number(

      result

        ?.forensic_analysis

        ?.risk_score || 0

    );





  const safeRiskScore =

    Math.max(

      0,

      Math.min(

        100,

        riskScore

      )

    );





  // =======================================================

  // Render

  // =======================================================



  return (



    <div className="app-shell">





      {/* =================================================

          NAVIGATION

          ================================================= */}



      <header className="topbar">



        <div

          className="brand"

          onClick={() => {



            setPage("scanner");



            setResult(null);



          }}

        >



          <div className="brand-icon">



            <ShieldCheck size={25} />



          </div>



          <div>



            <div className="brand-name">

              ScamScan

            </div>



            <div className="brand-subtitle">

              DIGITAL DOCUMENT FORENSICS

            </div>



          </div>



        </div>





        <div className="nav-actions">



          <button

            className={

              page === "scanner"

                ? "nav-button active"

                : "nav-button"

            }

            onClick={() => {



              setPage("scanner");



            }}

          >



            <ScanLine size={16} />



            Scanner



          </button>





          <button

            className={

              page === "history"

                ? "nav-button active"

                : "nav-button"

            }

            onClick={() => {



              setPage("history");



              fetchHistory();



            }}

          >



            <History size={16} />



            History



          </button>



        </div>





        <div className="system-status">



          <span className="status-dot"></span>



          Forensic Engine Online



        </div>



      </header>





      {/* =================================================

          MAIN

          ================================================= */}



      <main className="main-container">





        {/* =================================================

            HISTORY

            ================================================= */}



        {page === "history" && (



          <HistoryPage

            history={history}

            loading={historyLoading}

            error={historyError}

            opening={openingHistory}

            onRefresh={fetchHistory}

            onOpen={openHistoryScan}

            onBack={() =>

              setPage("scanner")

            }

          />



        )}





        {/* =================================================

            SCANNER

            ================================================= */}



        {page === "scanner" && (



          <>



            {!result && (



              <>



                <section className="hero-section">



                  <div className="hero-badge">



                    <ScanLine size={15} />



                    DOCUMENT FORENSIC ANALYSIS



                  </div>





                  <h1>



                    Detect suspicious



                    <span>

                      {" "}digital documents.

                    </span>



                  </h1>





                  <p>



                    Analyze document images using

                    compression analysis, structural

                    edge detection, forensic heatmaps

                    and OCR.



                  </p>



                </section>





                <section className="upload-card">



                  <div

                    className={

                      dragActive

                        ? "drop-zone drag-active"

                        : "drop-zone"

                    }

                    onDragOver={handleDragOver}

                    onDragLeave={handleDragLeave}

                    onDrop={handleDrop}

                    onClick={() =>

                      fileInputRef.current?.click()

                    }

                  >



                    <input

                      ref={fileInputRef}

                      type="file"

                      accept="image/jpeg,image/png,image/webp"

                      hidden

                      onChange={handleFileInput}

                    />





                    <div className="upload-icon">



                      <Upload size={30} />



                    </div>





                    <h2>

                      Drop your document here

                    </h2>





                    <p>

                      or click to browse from

                      your computer

                    </p>





                    <span className="supported-files">

                      JPG · JPEG · PNG · WEBP

                    </span>



                  </div>





                  {selectedFile && (



                    <div className="selected-file">



                      <div className="selected-preview">



                        <img

                          src={preview}

                          alt="Selected document"

                        />



                      </div>





                      <div className="file-information">



                        <div className="file-name">

                          {selectedFile.name}

                        </div>



                        <div className="file-size">



                          {(

                            selectedFile.size /

                            1024

                          ).toFixed(1)} KB



                        </div>



                      </div>





                      <button

                        className="remove-button"

                        onClick={clearFile}

                        type="button"

                      >



                        <X size={18} />



                      </button>



                    </div>



                  )}





                  {error && (



                    <div className="error-message">



                      <AlertTriangle size={18} />



                      <span>

                        {error}

                      </span>



                    </div>



                  )}





                  <button

                    className="analyze-button"

                    onClick={analyzeFile}

                    disabled={

                      !selectedFile ||

                      loading

                    }

                  >



                    {loading ? (



                      <>



                        <Loader2

                          className="spin"

                          size={20}

                        />



                        Running forensic analysis...



                      </>



                    ) : (



                      <>



                        <FileSearch size={20} />



                        Analyze Document



                      </>



                    )}



                  </button>





                  <div className="privacy-note">



                    <Lock size={14} />



                    Forensic analysis is performed

                    by ScamScan.



                  </div>



                </section>



              </>



            )}





            {result && (



              <ResultReport

                result={result}

                preview={preview}

                safeRiskScore={safeRiskScore}

                getRiskClass={getRiskClass}

                evidenceUrl={evidenceUrl}

                onNewScan={clearFile}

                setSelectedEvidence={

                  setSelectedEvidence

                }

              />



            )}



          </>



        )}



      </main>





      {/* =================================================

          EVIDENCE MODAL

          ================================================= */}



      {selectedEvidence && (



        <div

          className="evidence-modal"

          onClick={() =>

            setSelectedEvidence(null)

          }

        >



          <div

            className="evidence-modal-content"

            onClick={(event) =>

              event.stopPropagation()

            }

          >



            <button

              className="modal-close"

              onClick={() =>

                setSelectedEvidence(null)

              }

            >



              <X size={20} />



            </button>





            <div className="modal-title">



              <span>

                FORENSIC EVIDENCE

              </span>



              <h2>

                {selectedEvidence.title}

              </h2>



            </div>





            <div className="modal-image">



              <img

                src={selectedEvidence.image}

                alt={selectedEvidence.title}

              />



            </div>





            <p className="modal-explanation">



              {selectedEvidence.explanation}



            </p>



          </div>



        </div>



      )}





      <footer className="footer">



        <span>

          ScamScan

        </span>



        <span>

          Digital Document Forensics

        </span>



        <span>

          Preliminary Analysis Engine

        </span>



      </footer>



    </div>

  );

}





// =========================================================

// HISTORY PAGE

// =========================================================



function HistoryPage({

  history,

  loading,

  error,

  opening,

  onRefresh,

  onOpen,

  onBack,

}) {



  return (



    <section className="history-page">



      <div className="history-header">



        <div>



          <div className="hero-badge">



            <Database size={15} />



            SUPABASE SCAN ARCHIVE



          </div>





          <h1>

            Scan History

          </h1>





          <p>

            Review previous forensic analyses

            and reopen their reports.

          </p>



        </div>





        <div className="history-actions">



          <button

            className="secondary-button"

            onClick={onRefresh}

            disabled={loading}

          >



            <RefreshCw

              size={16}

              className={

                loading

                  ? "spin"

                  : ""

              }

            />



            Refresh



          </button>





          <button

            className="new-scan-button"

            onClick={onBack}

          >



            <ScanLine size={16} />



            New Scan



          </button>



        </div>



      </div>





      {error && (



        <div className="error-message">



          <AlertTriangle size={18} />



          <span>

            {error}

          </span>



        </div>



      )}





      {loading && (



        <div className="history-loading">



          <Loader2

            size={28}

            className="spin"

          />



          <span>

            Loading scan history...

          </span>



        </div>



      )}





      {!loading &&

        history.length === 0 &&

        !error && (



          <div className="empty-history">



            <div className="empty-history-icon">



              <History size={28} />



            </div>





            <h2>

              No scans yet

            </h2>





            <p>

              Your completed forensic scans

              will appear here.

            </p>





            <button

              className="analyze-button small-button"

              onClick={onBack}

            >



              <ScanLine size={17} />



              Run Your First Scan



            </button>



          </div>



        )}





      {!loading &&

        history.length > 0 && (



          <div className="history-table-wrapper">



            <div className="history-count">



              <div>



                <strong>

                  {history.length}

                </strong>



                <span>

                  stored scans

                </span>



              </div>





              <div className="history-live">



                <span className="status-dot"></span>



                Supabase Connected



              </div>



            </div>





            <div className="history-table">



              <div className="history-table-head">



                <span>Scan</span>



                <span>Document</span>



                <span>Risk</span>



                <span>Date</span>



                <span>Action</span>



              </div>





              {history.map(

                (record, index) => (



                  <HistoryRow

                    key={

                      record.scan_id ||

                      index

                    }

                    record={record}

                    onOpen={onOpen}

                    opening={opening}

                  />



                )

              )}



            </div>



          </div>



        )}



    </section>

  );

}





// =========================================================

// HISTORY ROW

// =========================================================



function HistoryRow({

  record,

  onOpen,

  opening,

}) {



  const riskLevel =

    record

      ?.forensic_analysis

      ?.risk_level ||

    record?.risk_level ||

    "Unknown";





  const riskScore =

    record

      ?.forensic_analysis

      ?.risk_score ??

    record?.risk_score;





  const riskClass =

    riskLevel

      .toLowerCase()

      .includes("high")

      ? "risk-high"

      : riskLevel

        .toLowerCase()

        .includes("moderate")

        ? "risk-medium"

        : "risk-low";





  const createdAt =

    record.created_at

      ? new Date(

          record.created_at

        ).toLocaleString()

      : "Unknown";





  const fileSize =

    record.file?.size

      ? `${(

          record.file.size / 1024

        ).toFixed(1)} KB`

      : record.file_size

        ? `${(

            record.file_size / 1024

          ).toFixed(1)} KB`

        : "--";





  const filename =

    record.file?.filename ||

    record.filename ||

    "Unknown file";





  return (



    <div className="history-row">



      <div className="scan-id-cell">



        <div className="scan-id-icon">



          <FileSearch size={16} />



        </div>





        <div>



          <strong>

            {record.scan_id ||

              "Unknown"}

          </strong>



          <span>

            {fileSize}

          </span>



        </div>



      </div>





      <div className="document-cell">



        <strong>

          {filename}

        </strong>



        <span>



          {record.file?.width ||

            record.width ||

            "--"}



          {" × "}



          {record.file?.height ||

            record.height ||

            "--"}



        </span>



      </div>





      <div className="risk-cell">



        <strong className={riskClass}>

          {riskScore ?? "--"}

        </strong>



        <span className={riskClass}>

          {riskLevel}

        </span>



      </div>





      <div className="date-cell">



        <Clock3 size={14} />



        <span>

          {createdAt}

        </span>



      </div>





      <div className="history-action-cell">



        <button

          className="open-report-button"

          onClick={() =>

            onOpen(record.scan_id)

          }

          disabled={opening}

        >



          {opening ? (



            <Loader2

              size={15}

              className="spin"

            />



          ) : (



            <FileText size={15} />



          )}



          Open Report



        </button>



      </div>



    </div>

  );

}





// =========================================================

// RESULT REPORT

// =========================================================



function ResultReport({

  result,

  preview,

  safeRiskScore,

  getRiskClass,

  evidenceUrl,

  onNewScan,

  setSelectedEvidence,

}) {

  // Build a plain-language explanation so the exported report is useful
  // to people who do not know digital-forensics terminology.
  const reportRiskLevel =
    result.forensic_analysis?.risk_level || "Unknown";
  const reportFindings = Array.isArray(result.findings)
    ? result.findings
    : [];
  // Pretrained model output is kept separate from heuristic screening.
  // The raw logit is not a verified fake-image probability.
  const pretrainedModel = result.ai_analysis?.pretrained_model;
  const modelAvailable = pretrainedModel?.available === true;
  const modelStatus = result.ai_analysis?.model_status || "Not available";
  const rawModelOutput = pretrainedModel?.raw_output;
  const rawModelText = rawModelOutput == null
    ? "Not available"
    : JSON.stringify(rawModelOutput);
  const aiScore = Number(result.ai_analysis?.ai_likelihood_score);
  const hasAiScore = Number.isFinite(aiScore);
  const elaScore =
    result.forensic_analysis?.ela_analysis?.ela_score;
  const edgeScore =
    result.forensic_analysis?.edge_analysis?.edge_score;
  const heatmapScore =
    result.forensic_analysis?.heatmap_analysis?.heatmap_score;
  const ocrText = result.ocr_analysis?.text || "";
  const fileName =
    result.file?.filename || result.filename || "Uploaded file";
  const riskExplanation = (() => {
    const level = String(reportRiskLevel).toLowerCase();
    if (level.includes("high")) {
      return "The current pipeline found enough indicators to place this file in its higher-risk category. Review the individual findings and visual evidence carefully. This is a reason to investigate further, not proof that the file is fraudulent.";
    }
    if (level.includes("medium") || level.includes("moderate")) {
      return "Some indicators deserve a closer look. Compare the highlighted evidence with the original file and verify important details with the issuing organisation before trusting it.";
    }
    if (level.includes("low")) {
      return "The current pipeline assigned a low risk level based on the indicators it measures. This does not certify that the file is genuine; some edits or fraud methods may not be detected.";
    }
    return "The system could not provide a recognised risk category. Review the available measurements and findings manually.";
  })();

  return (



    <section className="results-section">





      <div className="result-header">



        <div>



          <div className="hero-badge">



            <CheckCircle2 size={15} />



            ANALYSIS COMPLETE



          </div>





          <h2>

            Forensic Analysis Report

          </h2>





          <p>

            {result.file?.filename ||

              result.filename ||

              "Historical scan"}

          </p>



        </div>





        <div className="result-header-actions">
          <button
            className="secondary-button print-report-button"
            onClick={() => window.print()}
            type="button"
          >
            <Printer size={17} />
            Export PDF
          </button>

          <button
            className="new-scan-button"
            onClick={onNewScan}
            type="button"
          >
            <Upload size={17} />
            New Scan
          </button>
        </div>



      </div>





      <div className="report-meta">



        <div>



          <Clock3 size={15} />



          <span>



            {result.created_at

              ? new Date(

                  result.created_at

                ).toLocaleString()

              : "Analysis completed"}



          </span>



        </div>





        <div>



          <FileText size={15} />



          <span>

            {result.scan_id}

          </span>



        </div>



      </div>





      {/* Plain-language summary is included in the printable report. */}
      <section className="report-explainer">
        <div className="report-explainer-heading">
          <span>READ THIS FIRST</span>
          <h3>What does this result mean?</h3>
          <p>
            This section translates the technical measurements into everyday
            language. It describes what ScamScan observed in this upload and
            what those observations can — and cannot — tell you.
          </p>
        </div>

        <div className="report-explainer-summary">
          <strong>Summary for this file</strong>
          <p>
            ScamScan analysed <b>{fileName}</b> and assigned a preliminary
            risk level of <b>{reportRiskLevel}</b> with a score of{" "}
            <b>{Number(safeRiskScore).toFixed(1)} out of 100</b>.
            {" "}{riskExplanation}
          </p>
        </div>

        <div className="report-explainer-grid">
          <article>
            <h4>1. Risk score</h4>
            <p>
              This score combines indicators from the current analysis
              pipeline. It is a screening aid, not a probability that the
              document is fake and not a final authenticity verdict.
            </p>
          </article>
          <article>
            <h4>2. Error Level Analysis (ELA)</h4>
            <p>
              ELA looks for differences in how parts of an image respond to
              JPEG recompression. Unusual differences can happen after editing,
              but can also be caused by normal saving, resizing, screenshots,
              or different image regions. It cannot prove manipulation by itself.
            </p>
            <span className="report-measured-value">
              Measured indicator: {elaScore ?? "Not available"}
            </span>
          </article>
          <article>
            <h4>3. Edge analysis</h4>
            <p>
              Edge analysis highlights sharp boundaries such as letters,
              document borders, logos, and signatures. It measures visual
              structure; a higher or lower value alone does not mean fraud.
            </p>
            <span className="report-measured-value">
              Measured indicator: {edgeScore ?? "Not available"}
            </span>
          </article>
          <article>
            <h4>4. Heatmap</h4>
            <p>
              The heatmap makes areas with stronger pixel activity easier to
              locate. Highlighted regions are places to inspect, not automatic
              proof that something was pasted, erased, or changed.
            </p>
            <span className="report-measured-value">
              Activity indicator: {heatmapScore ?? "Not available"}
            </span>
          </article>
          <article>
            <h4>5. AI-generation screening</h4>
            <p>
              {hasAiScore
                ? `The preliminary heuristic AI-likelihood score is ${aiScore.toFixed(1)} out of 100, based on resolution, compression, noise, and texture. ${modelAvailable ? "A separate pretrained model inference was completed; its raw output is displayed below without assigning an unverified probability." : "Pretrained model inference was not available for this scan."} Neither result establishes whether the image is AI-generated or authentic.`
                : "AI-generation screening was not available for this scan. ScamScan cannot draw an AI-generation conclusion from this report."}
            </p>
          </article>
          <article>
            <h4>6. Text recognition (OCR)</h4>
            <p>
              OCR attempts to read text visible in the upload. It can help
              surface names, amounts, dates, and document wording, but it may
              misread characters or miss text. Always compare extracted text
              with the original.
            </p>
            <span className="report-measured-value">
              Text detected: {ocrText.trim() ? "Yes" : "No readable text returned"}
            </span>
          </article>
        </div>

        <div className="report-findings-explainer">
          <h4>What ScamScan reported for this upload</h4>
          {reportFindings.length > 0 ? (
            <ul>
              {reportFindings.map((finding, index) => (
                <li key={`plain-finding-${index}`}>{finding}</li>
              ))}
            </ul>
          ) : (
            <p>
              No separate finding messages were returned by the analysis
              pipeline. This does not guarantee that the file is authentic.
            </p>
          )}
        </div>

        <div className="report-next-steps">
          <h4>What should you do next?</h4>
          <ol>
            <li>Compare the original file with the evidence images in this report.</li>
            <li>Check any suspicious text, amount, date, signature, or logo against a trusted source.</li>
            <li>For payment receipts or bank documents, verify the transaction directly with the bank or payment provider.</li>
            <li>If the document affects money, identity, or legal decisions, do not rely on this score alone; seek independent verification.</li>
          </ol>
        </div>

        <p className="report-plain-language-note">
          Important: ScamScan identifies preliminary technical indicators. A
          low score does not prove a file is genuine, and a high score does not
          prove fraud. Results depend on image quality, compression, format,
          and the methods used to create or edit the file.
        </p>
      </section>

      {/* =================================================

          RISK

          ================================================= */}



      <section className="risk-overview">



        <div className="risk-main-card">



          <div>



            <span className="section-label">

              PRELIMINARY RISK ASSESSMENT

            </span>





            <div

              className={

                `risk-number ${

                  getRiskClass(

                    result

                      .forensic_analysis

                      ?.risk_level

                  )

                }`

              }

            >



              {safeRiskScore.toFixed(1)}



            </div>





            <div

              className={

                `risk-status ${

                  getRiskClass(

                    result

                      .forensic_analysis

                      ?.risk_level

                  )

                }`

              }

            >



              {result

                .forensic_analysis

                ?.risk_level ||

                "Unknown"}



            </div>





            <p>

              Combined indicator score from

              the current forensic pipeline.

            </p>



          </div>





          <div

            className={

              `risk-ring ${

                getRiskClass(

                  result

                    .forensic_analysis

                    ?.risk_level

                )

              }`

            }

            style={{

              "--risk-progress":

                `${safeRiskScore * 3.6}deg`,

            }}

          >



            <div className="risk-ring-inner">



              <strong>

                {Math.round(

                  safeRiskScore

                )}

              </strong>



              <span>

                / 100

              </span>



            </div>



          </div>



        </div>





        <MetricCard

          icon={<Activity size={21} />}

          label="ELA SCORE"

          value={

            result

              .forensic_analysis

              ?.ela_analysis

              ?.ela_score ?? "--"

          }

          description="Compression difference indicator"

        />





        <MetricCard

          icon={<Activity size={21} />}

          label="EDGE SCORE"

          value={

            result

              .forensic_analysis

              ?.edge_analysis

              ?.edge_score ?? "--"

          }

          description="Structural edge activity"

        />





        <MetricCard

          icon={<Search size={21} />}

          label="HEATMAP"

          value={

            result

              .forensic_analysis

              ?.heatmap_analysis

              ?.heatmap_score ?? "--"

          }

          description="High-activity ratio"

        />



      </section>






      {/* =================================================
          AI GENERATION INDICATOR
          ================================================= */}

      <section className="ai-detection-section">
        <div className="section-heading ai-section-heading">
          <div>
            <span>AI GENERATION ANALYSIS</span>
            <h3>AI Image Detection</h3>
          </div>

          <div className="ai-engine-badge">
            <Bot size={17} />
            PRELIMINARY
          </div>
        </div>

        {result.ai_analysis ? (
          <div className="ai-detection-grid">
            <div className="ai-main-card">
              <div className="ai-main-top">
                <div>
                  <span className="ai-label">AI LIKELIHOOD</span>

                  <div className="ai-score-row">
                    <strong>
                      {Number(
                        result.ai_analysis.ai_likelihood_score ?? 0
                      ).toFixed(1)}
                    </strong>
                    <span>/ 100</span>
                  </div>

                  <div className="ai-likelihood">
                    {result.ai_analysis.likelihood || "Unknown"}
                  </div>
                </div>

                <div
                  className="ai-score-ring"
                  style={{
                    "--ai-progress": `${
                      Math.max(
                        0,
                        Math.min(
                          100,
                          Number(
                            result.ai_analysis.ai_likelihood_score ?? 0
                          )
                        )
                      ) * 3.6
                    }deg`,
                  }}
                >
                  <div className="ai-score-ring-inner">
                    <BrainCircuit size={27} />
                  </div>
                </div>
              </div>

              <div className="ai-progress-track">
                <div
                  className="ai-progress-fill"
                  style={{
                    width: `${Math.max(
                      0,
                      Math.min(
                        100,
                        Number(
                          result.ai_analysis.ai_likelihood_score ?? 0
                        )
                      )
                    )}%`,
                  }}
                />
              </div>

              <p className="ai-main-description">
                This score represents preliminary forensic signals that
                can sometimes appear in AI-generated imagery.
              </p>
            </div>

            <div className="ai-signals-card">
              <div className="ai-card-title">
                <Cpu size={18} />
                <div>
                  <span>FORENSIC SIGNALS</span>
                  <h4>Detection Indicators</h4>
                </div>
              </div>

              <AISignal
                label="Resolution"
                value={
                  result.ai_analysis.signals
                    ?.resolution_indicator ?? 0
                }
              />

              <AISignal
                label="Compression"
                value={
                  result.ai_analysis.signals
                    ?.compression_indicator ?? 0
                }
              />

              <AISignal
                label="Noise"
                value={
                  result.ai_analysis.signals?.noise_indicator ?? 0
                }
              />

              <AISignal
                label="Texture"
                value={
                  result.ai_analysis.signals
                    ?.texture_indicator ?? 0
                }
              />
            </div>
          </div>
        ) : (
          <div className="ai-unavailable">
            <Bot size={22} />
            <div>
              <strong>AI generation analysis unavailable</strong>
              <span>
                This historical scan was created before the AI detection
                module was enabled.
              </span>
            </div>
          </div>
        )}

        {/* Model inference is reported independently from the heuristic score. */}
        {result.ai_analysis && (
          <div className="ai-signals-card ai-pretrained-card" style={{ marginTop: 20 }}>
            <div className="ai-card-title">
              <Cpu size={18} />
              <div>
                <span>PRETRAINED MODEL</span>
                <h4>GPU Model Inference</h4>
              </div>
            </div>
            <div className="ai-model-status-row" style={{ display: "flex", justifyContent: "space-between", gap: 16, padding: "12px 0", borderBottom: "1px solid rgba(148,163,184,.18)", flexWrap: "wrap" }}>
              <span>Connection</span>
              <strong>{modelStatus}</strong>
            </div>
            <div className="ai-model-status-row" style={{ display: "flex", justifyContent: "space-between", gap: 16, padding: "12px 0", borderBottom: "1px solid rgba(148,163,184,.18)", flexWrap: "wrap" }}>
              <span>Inference</span>
              <strong>{modelAvailable ? "Completed" : "Unavailable"}</strong>
            </div>
            <div className="ai-model-status-row" style={{ display: "flex", justifyContent: "space-between", gap: 16, padding: "12px 0", borderBottom: "1px solid rgba(148,163,184,.18)", flexWrap: "wrap" }}>
              <span>Model</span>
              <strong className="ai-model-name" style={{ overflowWrap: "anywhere", textAlign: "right", maxWidth: "100%" }}>
                {pretrainedModel?.model || "Not available"}
              </strong>
            </div>
            <div className="ai-model-status-row" style={{ display: "flex", justifyContent: "space-between", gap: 16, padding: "12px 0", borderBottom: "1px solid rgba(148,163,184,.18)", flexWrap: "wrap" }}>
              <span>Device</span>
              <strong>{pretrainedModel?.device || "Not available"}</strong>
            </div>
            <div className="ai-model-output" style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 18 }}>
              <span className="ai-label">RAW MODEL OUTPUT (UNINTERPRETED)</span>
              <code style={{ display: "block", padding: 14, borderRadius: 10, background: "rgba(127,127,127,.1)", overflowWrap: "anywhere", whiteSpace: "pre-wrap" }}>{rawModelText}</code>
            </div>
            <p className="ai-main-description" style={{ marginTop: 14 }}>
              {pretrainedModel?.interpretation ||
                "Raw model output is not a validated AI-generation probability or an authenticity verdict."}
            </p>
          </div>
        )}

        {result.ai_analysis?.note && (
          <div className="ai-disclaimer">
            <AlertTriangle size={16} />
            <span>{result.ai_analysis.note}</span>
          </div>
        )}
      </section>

      {/* =================================================

          SOURCE DOCUMENT

          ================================================= */}



      <section className="document-section">



        <div className="section-heading">



          <div>



            <span>

              SOURCE DOCUMENT

            </span>



            <h3>

              Original Image

            </h3>



          </div>



          <ImageIcon size={21} />



        </div>





        <div className="original-document-card">



          {preview ? (



            <img

              src={preview}

              alt="Original uploaded document"

            />



          ) : (



            <div className="historical-original">



              <FileText size={35} />



              <strong>

                Original upload not available

              </strong>



              <span>

                This report was opened from

                scan history. The forensic

                evidence remains available below.

              </span>



            </div>



          )}



        </div>



      </section>





      {/* =================================================

          FORENSIC EVIDENCE

          ================================================= */}



      <section className="evidence-section">



        <div className="section-heading">



          <div>



            <span>

              FORENSIC EVIDENCE

            </span>



            <h3>

              Visual Analysis

            </h3>



          </div>



          <ShieldCheck size={21} />



        </div>





        <div className="evidence-grid">



          <EvidenceCard

            title="Error Level Analysis"

            shortTitle="ELA"

            description="Compression Difference"

            explanation={

              "ELA compares the document with a JPEG-recompressed version. Regions that behave differently can become more visible. These differences are investigative clues, not proof of editing."

            }

            image={

              evidenceUrl(

                result

                  .visual_evidence

                  ?.ela

                  ?.url

              )

            }

            metric={

              result

                .forensic_analysis

                ?.ela_analysis

                ?.ela_score

            }

            metricLabel="ELA indicator"

            onOpen={() =>

              setSelectedEvidence({

                title:

                  "Error Level Analysis",

                image:

                  evidenceUrl(

                    result

                      .visual_evidence

                      ?.ela

                      ?.url

                  ),

                explanation:

                  "ELA highlights differences in JPEG recompression behaviour. Areas with unusual differences may deserve closer investigation.",

              })

            }

          />





          <EvidenceCard

            title="Edge Detection"

            shortTitle="EDGES"

            description="Structural Activity"

            explanation={

              "The edge map highlights strong changes in pixel intensity such as text, borders, contours, logos and signatures."

            }

            image={

              evidenceUrl(

                result

                  .visual_evidence

                  ?.edges

                  ?.url

              )

            }

            metric={

              result

                .forensic_analysis

                ?.edge_analysis

                ?.edge_score

            }

            metricLabel="Edge indicator"

            onOpen={() =>

              setSelectedEvidence({

                title:

                  "Edge Detection",

                image:

                  evidenceUrl(

                    result

                      .visual_evidence

                      ?.edges

                      ?.url

                  ),

                explanation:

                  "Edge detection reveals structural boundaries and high-frequency details within the document.",

              })

            }

          />





          <EvidenceCard

            title="Forensic Heatmap"

            shortTitle="HEATMAP"

            description="Activity Visualization"

            explanation={

              "The heatmap visualizes regions with elevated pixel activity. Highlighted regions should be reviewed alongside the original document."

            }

            image={

              evidenceUrl(

                result

                  .visual_evidence

                  ?.heatmap

                  ?.url

              )

            }

            metric={

              result

                .forensic_analysis

                ?.heatmap_analysis

                ?.heatmap_score

            }

            metricLabel="Activity ratio"

            onOpen={() =>

              setSelectedEvidence({

                title:

                  "Forensic Heatmap",

                image:

                  evidenceUrl(

                    result

                      .visual_evidence

                      ?.heatmap

                      ?.url

                  ),

                explanation:

                  "The heatmap helps investigators quickly identify areas that may deserve closer visual inspection.",

              })

            }

          />



        </div>



      </section>





      {/* =================================================

          OCR + FINDINGS

          ================================================= */}



      <section className="analysis-columns">



        <div className="panel">



          <div className="panel-header">



            <div>



              <span>

                OCR ANALYSIS

              </span>



              <h3>

                Extracted Text

              </h3>



            </div>



            <FileSearch size={20} />



          </div>





          <div className="ocr-stats">



            <div>



              <strong>

                {result

                  .ocr_analysis

                  ?.word_count ?? 0}

              </strong>



              <span>

                Words

              </span>



            </div>





            <div>



              <strong>

                {result

                  .ocr_analysis

                  ?.character_count ?? 0}

              </strong>



              <span>

                Characters

              </span>



            </div>





            <div>



              <strong>

                {result

                  .ocr_analysis

                  ?.confidence ??

                  "--"}

                %

              </strong>



              <span>

                Confidence

              </span>



            </div>



          </div>





          <pre className="ocr-box">



            {result

              .ocr_analysis

              ?.text ||

              "No readable text detected."}



          </pre>





          <div className="ocr-note">



            OCR results may contain recognition

            errors and should be verified against

            the original document.



          </div>



        </div>





        <div className="panel">



          <div className="panel-header">



            <div>



              <span>

                FORENSIC FINDINGS

              </span>



              <h3>

                Analysis Summary

              </h3>



            </div>



            <ShieldCheck size={20} />



          </div>





          <div className="findings-list">



            {result.findings?.map(

              (finding, index) => (



                <div

                  className="finding"

                  key={index}

                >



                  <CheckCircle2 size={17} />



                  <span>

                    {finding}

                  </span>



                </div>



              )

            )}



          </div>



        </div>



      </section>





      {/* =================================================

          SCAN INFORMATION

          ================================================= */}



      <section className="scan-info">



        <div>



          <span>

            SCAN ID

          </span>



          <strong>

            {result.scan_id}

          </strong>



        </div>





        <div>



          <span>

            FILE SIZE

          </span>



          <strong>



            {(

              (result.file?.size ||

                result.file_size ||

                0) /

              1024

            ).toFixed(1)} KB



          </strong>



        </div>





        <div>



          <span>

            DIMENSIONS

          </span>



          <strong>



            {result.file?.width ||

              result.width ||

              "--"}



            {" × "}



            {result.file?.height ||

              result.height ||

              "--"}



          </strong>



        </div>





        <div>



          <span>

            OCR ENGINE

          </span>



          <strong>



            {result

              .ocr_analysis

              ?.engine ||

              "Tesseract OCR"}



          </strong>



        </div>



      </section>





      {/* =================================================

          DISCLAIMER

          ================================================= */}



      <div className="disclaimer">



        <AlertTriangle size={18} />



        <div>



          <strong>

            Important forensic limitation

          </strong>



          <span>



            {result.disclaimer ||

              "ELA, edge analysis, heatmaps and OCR provide investigative indicators only. They do not prove that an image is genuine or forged."}



          </span>



        </div>



      </div>



    </section>

  );

}






// =========================================================
// AI Signal
// =========================================================

function AISignal({ label, value }) {
  const safeValue = Math.max(
    0,
    Math.min(100, Number(value) || 0)
  );

  return (
    <div className="ai-signal">
      <div className="ai-signal-header">
        <span>{label}</span>
        <strong>{safeValue.toFixed(1)}</strong>
      </div>

      <div className="ai-signal-track">
        <div
          className="ai-signal-fill"
          style={{ width: `${safeValue}%` }}
        />
      </div>
    </div>
  );
}

// =========================================================

// Metric Card

// =========================================================



function MetricCard({

  icon,

  label,

  value,

  description,

}) {



  return (



    <div className="metric-card">



      <div className="metric-icon">

        {icon}

      </div>



      <div className="card-label">

        {label}

      </div>



      <strong>

        {value}

      </strong>



      <span>

        {description}

      </span>



    </div>

  );

}





// =========================================================

// Evidence Card

// =========================================================



function EvidenceCard({

  title,

  shortTitle,

  description,

  explanation,

  image,

  metric,

  metricLabel,

  onOpen,

}) {



  return (



    <article className="evidence-card">



      <div className="evidence-image">



        {image ? (



          <img

            src={image}

            alt={title}

          />



        ) : (



          <div className="image-placeholder">

            Evidence unavailable

          </div>



        )}





        {image && (



          <button

            className="evidence-expand"

            onClick={onOpen}

            type="button"

          >



            <Maximize2 size={17} />



          </button>



        )}



      </div>





      <div className="evidence-information">



        <div className="evidence-title-row">



          <div>



            <span className="evidence-code">

              {shortTitle}

            </span>



            <h4>

              {title}

            </h4>



            <p>

              {description}

            </p>



          </div>



          <ShieldCheck size={18} />



        </div>





        <div className="evidence-metric">



          <span>

            {metricLabel}

          </span>



          <strong>

            {metric ?? "--"}

          </strong>



        </div>





        <p className="evidence-explanation">

          {explanation}

        </p>



      </div>



    </article>

  );

}

export default App;