import React, { useState, useMemo } from "react";
import {
  TrendUp,
  TrendDown,
  ArrowCounterClockwise,
  DownloadSimple,
  Eye,
  Warning,
  CaretUp,
  CaretDown,
  SlidersHorizontal,
  X,
} from "@phosphor-icons/react";

// ── Types ─────────────────────────────────────────────────────────────────────

interface JobInfo {
  title: string;
  total_required_skills?: number;
  experience_level?: string;
}

interface RankedCandidate {
  candidate_id: string;
  name: string;
  email: string;
  match_score: number;
  skill_coverage?: number;
  matched_skills?: number;
  total_required_skills?: number;
  explanation: string;
}

interface ProcessingError {
  filename: string;
  error: string;
}

interface AnalysisResults {
  job_id: string;
  job_info: JobInfo;
  total_resumes?: number;
  successfully_processed?: number;
  processing_errors?: ProcessingError[];
  ranked_candidates: RankedCandidate[];
  processing_time?: string;
}

interface ResultsTableProps {
  results: AnalysisResults;
  onReset: () => void;
}

type SortField = "match_score" | "name" | "skill_coverage" | "matched_skills";
type SortDirection = "asc" | "desc";
type ScoreFilter = "all" | "strong" | "good" | "partial" | "poor";

// ── Helpers ───────────────────────────────────────────────────────────────────

const getScoreColors = (score: number) => {
  if (score >= 80) return { chip: "bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300", bar: "bg-emerald-500" };
  if (score >= 60) return { chip: "bg-indigo-100 dark:bg-indigo-950/60 text-indigo-800 dark:text-indigo-300",   bar: "bg-indigo-500"  };
  if (score >= 40) return { chip: "bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300",     bar: "bg-amber-500"   };
  return               { chip: "bg-red-100 dark:bg-red-950/60 text-red-800 dark:text-red-300",            bar: "bg-red-500"     };
};

const getMatchLabel = (score: number) => {
  if (score >= 80) return "Strong Match";
  if (score >= 60) return "Good Match";
  if (score >= 40) return "Partial Match";
  return "Poor Match";
};

const getInitials = (name: string) =>
  name.split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2);

const getRankBadge = (index: number) => {
  const medals = ["🥇", "🥈", "🥉"];
  if (index < 3) return <span className="text-lg">{medals[index]}</span>;
  return <span className="text-sm font-medium text-gray-400 dark:text-gray-500">#{index + 1}</span>;
};

// ── Reusable Progress Bar ─────────────────────────────────────────────────────

const ScoreBar: React.FC<{ score: number }> = ({ score }) => (
  <div className="w-full bg-gray-100 dark:bg-gray-800 rounded-full h-1.5 overflow-hidden">
    <div
      className={`h-full rounded-full transition-all ${getScoreColors(score).bar}`}
      style={{ width: `${Math.min(score, 100)}%` }}
    />
  </div>
);

// ── Component ─────────────────────────────────────────────────────────────────

const ResultsTable: React.FC<ResultsTableProps> = ({ results, onReset }) => {
  const [sortField, setSortField]         = useState<SortField>("match_score");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");
  const [selectedCandidate, setSelectedCandidate] = useState<RankedCandidate | null>(null);
  const [showFilters, setShowFilters]     = useState(false);
  const [scoreFilter, setScoreFilter]     = useState<ScoreFilter>("all");

  // ── Sort + filter ──────────────────────────────────────────────────────────
  const sortedCandidates = useMemo(() => {
    let filtered = results.ranked_candidates;
    if (scoreFilter !== "all") {
      filtered = filtered.filter(c => {
        const s = c.match_score;
        if (scoreFilter === "strong")  return s >= 80;
        if (scoreFilter === "good")    return s >= 60 && s < 80;
        if (scoreFilter === "partial") return s >= 40 && s < 60;
        if (scoreFilter === "poor")    return s < 40;
        return true;
      });
    }
    return [...filtered].sort((a, b) => {
      let av: string | number, bv: string | number;
      switch (sortField) {
        case "name":           av = a.name.toLowerCase(); bv = b.name.toLowerCase(); break;
        case "match_score":    av = a.match_score;        bv = b.match_score;        break;
        case "skill_coverage": av = a.skill_coverage ?? 0; bv = b.skill_coverage ?? 0; break;
        case "matched_skills": av = a.matched_skills ?? 0; bv = b.matched_skills ?? 0; break;
        default: return 0;
      }
      if (typeof av === "string") {
        return sortDirection === "asc" ? av.localeCompare(bv as string) : (bv as string).localeCompare(av);
      }
      return sortDirection === "asc" ? av - (bv as number) : (bv as number) - av;
    });
  }, [results.ranked_candidates, sortField, sortDirection, scoreFilter]);

  const handleSort = (field: SortField) => {
    if (sortField === field) setSortDirection(d => d === "asc" ? "desc" : "asc");
    else { setSortField(field); setSortDirection(field === "name" ? "asc" : "desc"); }
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field)
      return <CaretDown size={12} className="inline ml-1 opacity-30" />;
    return sortDirection === "asc"
      ? <CaretUp   size={12} className="inline ml-1 text-indigo-500" weight="bold" />
      : <CaretDown size={12} className="inline ml-1 text-indigo-500" weight="bold" />;
  };

  // ── CSV Export ─────────────────────────────────────────────────────────────
  const exportResults = () => {
    try {
      const headers = ["Rank","Name","Email","Match Score (%)","Skill Coverage (%)","Matched Skills","Total Required Skills","Match Category","Explanation"];
      const rows = sortedCandidates.map((c, i) => [
        (i + 1).toString(), c.name || "Unknown", c.email || "No email",
        c.match_score.toFixed(1), (c.skill_coverage ?? 0).toFixed(1),
        (c.matched_skills ?? 0).toString(), (c.total_required_skills ?? 0).toString(),
        getMatchLabel(c.match_score),
        (c.explanation || "").replace(/\*\*(.*?)\*\*/g, "$1").replace(/"/g, '""'),
      ]);
      const csv = [headers, ...rows].map(r => r.map(c => `"${c}"`).join(",")).join("\n");
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `cv-snap-${results.job_id}-${new Date().toISOString().slice(0,10)}.csv`;
      link.style.visibility = "hidden";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (e) { console.error(e); alert("CSV export failed."); }
  };

  // ── Stats ──────────────────────────────────────────────────────────────────
  const avgScore = sortedCandidates.length
    ? Math.round(sortedCandidates.reduce((s, c) => s + c.match_score, 0) / sortedCandidates.length) : 0;

  const stats = [
    { label: "Resumes Processed", value: results.successfully_processed ?? results.ranked_candidates.length, accent: "text-indigo-600 dark:text-indigo-400",  bg: "bg-indigo-50 dark:bg-indigo-950/40"  },
    { label: "Required Skills",   value: results.job_info.total_required_skills ?? "N/A",                    accent: "text-emerald-600 dark:text-emerald-400", bg: "bg-emerald-50 dark:bg-emerald-950/40" },
    { label: "Good+ Matches",     value: sortedCandidates.filter(c => c.match_score >= 60).length,           accent: "text-violet-600 dark:text-violet-400",  bg: "bg-violet-50 dark:bg-violet-950/40"  },
    { label: "Avg Score",         value: `${avgScore}%`,                                                      accent: "text-amber-600 dark:text-amber-400",   bg: "bg-amber-50 dark:bg-amber-950/40"   },
  ];

  const filterOptions: { key: ScoreFilter; label: string }[] = [
    { key: "all",     label: `All Candidates (${results.ranked_candidates.length})` },
    { key: "strong",  label: "Strong Match (80%+)"   },
    { key: "good",    label: "Good Match (60–79%)"   },
    { key: "partial", label: "Partial Match (40–59%)" },
    { key: "poor",    label: "Poor Match (<40%)"      },
  ];

  return (
    <div className="space-y-5">

      {/* ── Header Card ── */}
      <div className="bg-white dark:bg-gray-900/60 border border-gray-100 dark:border-gray-800/80 rounded-2xl shadow-sm p-6 backdrop-blur-sm">
        <div className="flex items-start justify-between flex-wrap gap-4 mb-6">
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <TrendUp size={22} weight="bold" className="text-indigo-500 dark:text-indigo-400" />
              Analysis Results
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Ranked candidates for:{" "}
              <span className="font-medium text-gray-700 dark:text-gray-300">{results.job_info.title}</span>
            </p>
          </div>
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={exportResults}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            >
              <DownloadSimple size={16} weight="bold" /> Export CSV
            </button>
            <button
              onClick={onReset}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
            >
              <ArrowCounterClockwise size={16} weight="bold" /> New Analysis
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {stats.map(s => (
            <div key={s.label} className={`${s.bg} rounded-xl p-4 text-center border border-transparent dark:border-gray-800/40`}>
              <div className={`text-2xl font-bold ${s.accent}`}>{s.value}</div>
              <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">{s.label}</div>
            </div>
          ))}
        </div>

        {/* Processing errors */}
        {results.processing_errors && results.processing_errors.length > 0 && (
          <div className="mt-4 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/50 rounded-xl p-4 flex items-start gap-2">
            <Warning size={18} weight="fill" className="text-amber-500 mt-0.5 shrink-0" />
            <div className="text-sm text-amber-800 dark:text-amber-300">
              <span className="font-medium">{results.processing_errors.length} file(s) couldn't be processed:</span>
              <ul className="mt-1 space-y-0.5">
                {results.processing_errors.map((e, i) => (
                  <li key={i}><span className="font-medium">{e.filename}:</span> {e.error}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* ── Filters ── */}
      <div className="bg-white dark:bg-gray-900/60 border border-gray-100 dark:border-gray-800/80 rounded-2xl shadow-sm overflow-hidden backdrop-blur-sm">
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="w-full px-6 py-4 flex items-center justify-between text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
        >
          <span className="flex items-center gap-2">
            <SlidersHorizontal size={16} weight="bold" className="text-gray-400" />
            Filters &amp; Sorting
          </span>
          {showFilters
            ? <CaretUp   size={16} className="text-gray-400" />
            : <CaretDown size={16} className="text-gray-400" />}
        </button>
        {showFilters && (
          <div className="px-6 pb-5 border-t border-gray-100 dark:border-gray-800 pt-4 flex flex-wrap items-end gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Filter by Score</label>
              <select
                value={scoreFilter}
                onChange={e => setScoreFilter(e.target.value as ScoreFilter)}
                className="px-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-300 dark:focus:ring-indigo-800"
              >
                {filterOptions.map(o => <option key={o.key} value={o.key}>{o.label}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Sort By</label>
              <select
                value={sortField}
                onChange={e => handleSort(e.target.value as SortField)}
                className="px-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-300 dark:focus:ring-indigo-800"
              >
                <option value="match_score">Match Score</option>
                <option value="skill_coverage">Skill Coverage</option>
                <option value="matched_skills">Matched Skills</option>
                <option value="name">Name (A–Z)</option>
              </select>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400 pb-1">
              Showing <span className="font-medium text-gray-700 dark:text-gray-300">{sortedCandidates.length}</span> of {results.ranked_candidates.length} candidates
            </p>
          </div>
        )}
      </div>

      {/* ── Table ── */}
      <div className="bg-white dark:bg-gray-900/60 border border-gray-100 dark:border-gray-800/80 rounded-2xl shadow-sm overflow-hidden backdrop-blur-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="bg-gray-50/80 dark:bg-gray-800/60 border-b border-gray-100 dark:border-gray-800">
                {[
                  { label: "Rank",        field: null             },
                  { label: "Candidate",   field: "name"           },
                  { label: "Match Score", field: "match_score"    },
                  { label: "Coverage",    field: "skill_coverage" },
                  { label: "Skills",      field: "matched_skills" },
                  { label: "Explanation", field: null             },
                  { label: "Actions",     field: null             },
                ].map(col => (
                  <th
                    key={col.label}
                    onClick={() => col.field && handleSort(col.field as SortField)}
                    className={`px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider
                      ${col.field ? "cursor-pointer hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors select-none" : ""}`}
                  >
                    {col.label}
                    {col.field && <SortIcon field={col.field as SortField} />}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50 dark:divide-gray-800/60">
              {sortedCandidates.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-16 text-center">
                    <TrendDown size={40} className="text-gray-200 dark:text-gray-700 mx-auto mb-3" />
                    <p className="text-sm text-gray-400 dark:text-gray-500">
                      {scoreFilter !== "all" ? "No candidates match this filter." : "No candidates were processed."}
                    </p>
                  </td>
                </tr>
              ) : sortedCandidates.map((c, index) => {
                const colors = getScoreColors(c.match_score);
                return (
                  <tr key={c.candidate_id} className="hover:bg-gray-50/60 dark:hover:bg-gray-800/40 transition-colors">
                    {/* Rank */}
                    <td className="px-4 py-4 text-center w-12">{getRankBadge(index)}</td>

                    {/* Candidate */}
                    <td className="px-4 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 flex items-center justify-center text-xs font-bold shrink-0">
                          {getInitials(c.name)}
                        </div>
                        <div>
                          <div className="text-sm font-semibold text-black dark:text-white">{c.name}</div>
                          <div className="text-xs text-gray-500 dark:text-gray-400">{c.email}</div>
                        </div>
                      </div>
                    </td>

                    {/* Score */}
                    <td className="px-4 py-4">
                      <div className="flex flex-col gap-1.5 min-w-[150px]">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-bold text-gray-800 dark:text-gray-200">{c.match_score.toFixed(1)}%</span>
                          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${colors.chip}`}>
                            {getMatchLabel(c.match_score)}
                          </span>
                        </div>
                        <ScoreBar score={c.match_score} />
                      </div>
                    </td>

                    {/* Coverage */}
                    <td className="px-4 py-4">
                      <span className="text-sm text-gray-700 dark:text-gray-300">{(c.skill_coverage ?? 0).toFixed(1)}%</span>
                    </td>

                    {/* Skills */}
                    <td className="px-4 py-4">
                      <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">{c.matched_skills ?? 0}</span>
                      <span className="text-xs text-gray-400 dark:text-gray-500">/{c.total_required_skills ?? 0}</span>
                    </td>

                    {/* Explanation */}
                    <td className="px-4 py-4 max-w-[240px]">
                      <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2 leading-relaxed">
                        {c.explanation.replace(/\*\*(.*?)\*\*/g, "$1")}
                      </p>
                    </td>

                    {/* Actions */}
                    <td className="px-4 py-4">
                      <button
                        onClick={() => setSelectedCandidate(c)}
                        className="flex items-center gap-1 text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 transition-colors"
                      >
                        <Eye size={14} weight="bold" /> View
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Candidate Detail Modal ── */}
      {selectedCandidate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setSelectedCandidate(null)} />
          <div className="relative bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto border border-gray-100 dark:border-gray-800">
            {/* Header */}
            <div className="flex items-start justify-between p-6 border-b border-gray-100 dark:border-gray-800">
              <div>
                <h3 className="text-lg font-bold text-black dark:text-white">{selectedCandidate.name}</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">{selectedCandidate.email}</p>
              </div>
              <button
                onClick={() => setSelectedCandidate(null)}
                className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <X size={20} weight="bold" />
              </button>
            </div>

            {/* Body */}
            <div className="p-6 space-y-5">
              {/* Score cards */}
              <div className="grid grid-cols-3 gap-3">
                {[
                  { label: "Overall Match",  value: `${selectedCandidate.match_score.toFixed(1)}%`, color: "text-indigo-600 dark:text-indigo-400",  bg: "bg-indigo-50 dark:bg-indigo-950/40"  },
                  { label: "Skill Coverage", value: `${(selectedCandidate.skill_coverage ?? 0).toFixed(1)}%`, color: "text-emerald-600 dark:text-emerald-400", bg: "bg-emerald-50 dark:bg-emerald-950/40" },
                  { label: "Skills Matched", value: `${selectedCandidate.matched_skills ?? 0}/${selectedCandidate.total_required_skills ?? 0}`, color: "text-violet-600 dark:text-violet-400", bg: "bg-violet-50 dark:bg-violet-950/40" },
                ].map(s => (
                  <div key={s.label} className={`${s.bg} rounded-xl p-4 text-center border border-transparent dark:border-gray-800/40`}>
                    <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">{s.label}</div>
                  </div>
                ))}
              </div>

              {/* Badge */}
              <div className="flex justify-center">
                <span className={`text-sm font-semibold px-4 py-1.5 rounded-full ${getScoreColors(selectedCandidate.match_score).chip}`}>
                  {getMatchLabel(selectedCandidate.match_score)}
                </span>
              </div>

              {/* Explanation */}
              <div>
                <h4 className="text-sm font-semibold text-gray-800 dark:text-gray-200 mb-2">Match Analysis</h4>
                <div
                  className="bg-gray-50 dark:bg-gray-950/60 border border-gray-100 dark:border-gray-800/80 rounded-xl p-4 text-sm text-gray-700 dark:text-gray-300 leading-relaxed"
                  dangerouslySetInnerHTML={{
                    __html: selectedCandidate.explanation
                      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900 dark:text-white">$1</strong>')
                      .replace(/\n/g, "<br>"),
                  }}
                />
              </div>

              {/* Recommendation */}
              {(() => {
                const s = selectedCandidate.match_score;
                const cfg = s >= 80
                  ? { bg: "bg-emerald-50 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-900/50", title: "text-emerald-800 dark:text-emerald-300", body: "text-emerald-700 dark:text-emerald-400", text: "Highly recommended for interview. Strong alignment with job requirements." }
                  : s >= 60
                  ? { bg: "bg-indigo-50 dark:bg-indigo-950/30 border-indigo-200 dark:border-indigo-900/50",   title: "text-indigo-800 dark:text-indigo-300",  body: "text-indigo-700 dark:text-indigo-400",  text: "Recommended for interview. Good potential with some development areas." }
                  : s >= 40
                  ? { bg: "bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-900/50",     title: "text-amber-800 dark:text-amber-300",   body: "text-amber-700 dark:text-amber-400",   text: "Consider if candidates are limited. May require significant training." }
                  : { bg: "bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-900/50",         title: "text-red-800 dark:text-red-300",     body: "text-red-700 dark:text-red-400",     text: "Not recommended unless role requirements change significantly." };
                return (
                  <div className={`rounded-xl border p-4 ${cfg.bg}`}>
                    <h5 className={`text-sm font-semibold mb-1 ${cfg.title}`}>Recommendation</h5>
                    <p className={`text-sm ${cfg.body}`}>{cfg.text}</p>
                  </div>
                );
              })()}
            </div>

            {/* Footer */}
            <div className="flex justify-end gap-2 p-6 border-t border-gray-100 dark:border-gray-800">
              <button
                onClick={() => setSelectedCandidate(null)}
                className="px-4 py-2 rounded-lg text-sm font-medium text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
              >
                Close
              </button>
              <button
                onClick={() => window.open(`mailto:${selectedCandidate.email}?subject=Interview Opportunity - ${results.job_info.title}`)}
                className="px-4 py-2 rounded-lg text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
              >
                Contact Candidate
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsTable;
