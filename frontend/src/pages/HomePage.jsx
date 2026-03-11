import { Link } from "react-router-dom";

function HomePage() {
  return (
    <div className="page-center">
      <header className="navbar">
        <div className="brand">Legal Query RAG</div>
        <div className="nav-actions">
          <Link className="btn btn-outline" to="/login">
            Login
          </Link>
          <Link className="btn btn-primary" to="/signup">
            Sign Up
          </Link>
        </div>
      </header>

      <section className="card hero-card">
        <p className="tag">Judicial Intelligence System</p>
        <h1>System-level legal query platform for reliable legal reasoning.</h1>
        <p className="subtitle">
          Legal Query RAG combines retrieval, legal knowledge grounding, and
          structured response generation to support legal teams with consistent,
          traceable, and context-aware answers.
        </p>

        <div className="hero-stats">
          <article className="stat-box">
            <p className="stat-label">System Scope</p>
            <p className="stat-value">End-to-End RAG</p>
          </article>
          <article className="stat-box">
            <p className="stat-label">Response Mode</p>
            <p className="stat-value">Grounded + Explainable</p>
          </article>
          <article className="stat-box">
            <p className="stat-label">Target Users</p>
            <p className="stat-value">Law Firms & Legal Teams</p>
          </article>
        </div>
      </section>

      <section className="system-grid">
        <article className="card system-card">
          <h2>Core Modules</h2>
          <ul>
            <li>Legal document ingestion and indexing pipeline</li>
            <li>Context retrieval and ranking engine</li>
            <li>Controlled answer generation with legal framing</li>
          </ul>
        </article>

        <article className="card system-card">
          <h2>Operating Workflow</h2>
          <ul>
            <li>Capture query intent and jurisdiction context</li>
            <li>Retrieve relevant legal passages and references</li>
            <li>Generate response with traceable supporting context</li>
          </ul>
        </article>

        <article className="card system-card">
          <h2>Governance & Trust</h2>
          <ul>
            <li>Access controls for legal stakeholders</li>
            <li>Session-based query handling and auditability</li>
            <li>Human review loop for critical legal outcomes</li>
          </ul>
        </article>
      </section>

      <section className="card final-cta">
        <h2>Start using Legal Query RAG as your legal intelligence front layer.</h2>
        <p className="subtitle">
          Onboard your team, centralize legal knowledge, and standardize
          high-quality legal responses across use cases.
        </p>
      </section>
    </div>
  );
}

export default HomePage;
