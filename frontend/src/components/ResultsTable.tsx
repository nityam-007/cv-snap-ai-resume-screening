import React, { useState, useMemo } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  User, 
  Mail, 
  Award, 
  Target,
  ChevronDown,
  ChevronUp,
  RotateCcw,
  Download,
  Eye,
  AlertTriangle
} from 'lucide-react';
import { AnalysisResults, RankedCandidate, getMatchScoreBadgeColor, getMatchLabel } from '../services/api';

interface ResultsTableProps {
  results: AnalysisResults;
  onReset: () => void;
}

type SortField = 'match_score' | 'name' | 'skill_coverage' | 'matched_skills';
type SortDirection = 'asc' | 'desc';

const ResultsTable: React.FC<ResultsTableProps> = ({ results, onReset }) => {
  const [sortField, setSortField] = useState<SortField>('match_score');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [selectedCandidate, setSelectedCandidate] = useState<RankedCandidate | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [scoreFilter, setScoreFilter] = useState<'all' | 'strong' | 'good' | 'partial' | 'poor'>('all');

  // Sort candidates
  const sortedCandidates = useMemo(() => {
    let filtered = results.ranked_candidates;

    // Apply score filter
    if (scoreFilter !== 'all') {
      filtered = filtered.filter(candidate => {
        const score = candidate.match_score;
        switch (scoreFilter) {
          case 'strong': return score >= 80;
          case 'good': return score >= 60 && score < 80;
          case 'partial': return score >= 40 && score < 60;
          case 'poor': return score < 40;
          default: return true;
        }
      });
    }

    // Sort
    return [...filtered].sort((a, b) => {
      let aValue: string | number;
      let bValue: string | number;

      switch (sortField) {
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'match_score':
          aValue = a.match_score;
          bValue = b.match_score;
          break;
        case 'skill_coverage':
          aValue = a.skill_coverage;
          bValue = b.skill_coverage;
          break;
        case 'matched_skills':
          aValue = a.matched_skills;
          bValue = b.matched_skills;
          break;
        default:
          return 0;
      }

      if (typeof aValue === 'string') {
        return sortDirection === 'asc' 
          ? aValue.localeCompare(bValue as string)
          : (bValue as string).localeCompare(aValue);
      } else {
        return sortDirection === 'asc' 
          ? aValue - (bValue as number)
          : (bValue as number) - aValue;
      }
    });
  }, [results.ranked_candidates, sortField, sortDirection, scoreFilter]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection(field === 'name' ? 'asc' : 'desc');
    }
  };

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />;
  };

  const exportResults = () => {
    const csvContent = [
      ['Rank', 'Name', 'Email', 'Match Score', 'Skill Coverage', 'Matched Skills', 'Total Required', 'Explanation'],
      ...sortedCandidates.map((candidate, index) => [
        index + 1,
        candidate.name,
        candidate.email,
        candidate.match_score.toFixed(1),
        candidate.skill_coverage.toFixed(1),
        candidate.matched_skills,
        candidate.total_required_skills,
        candidate.explanation.replace(/\*\*(.*?)\*\*/g, '$1') // Remove markdown
      ])
    ].map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cv-snap-results-${results.job_id}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-gray-900 flex items-center">
              <TrendingUp className="w-6 h-6 mr-2 text-blue-600" />
              Analysis Results
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Ranked candidates for: <span className="font-medium">{results.job_info.title}</span>
            </p>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={exportResults}
              className="flex items-center px-4 py-2 text-sm text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </button>
            <button
              onClick={onReset}
              className="flex items-center px-4 py-2 text-sm text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              New Analysis
            </button>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-blue-600">{results.successfully_processed}</div>
            <div className="text-sm text-blue-800">Resumes Processed</div>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-green-600">{results.job_info.total_required_skills}</div>
            <div className="text-sm text-green-800">Required Skills</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-purple-600">
              {sortedCandidates.filter(c => c.match_score >= 60).length}
            </div>
            <div className="text-sm text-purple-800">Good+ Matches</div>
          </div>
          <div className="bg-orange-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-orange-600">
              {Math.round(sortedCandidates.reduce((sum, c) => sum + c.match_score, 0) / sortedCandidates.length) || 0}%
            </div>
            <div className="text-sm text-orange-800">Avg Score</div>
          </div>
        </div>

        {/* Processing Errors */}
        {results.processing_errors.length > 0 && (
          <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start">
              <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5 mr-2 flex-shrink-0" />
              <div>
                <h4 className="text-sm font-medium text-yellow-800">Processing Warnings</h4>
                <div className="mt-2 text-sm text-yellow-700">
                  {results.processing_errors.length} file(s) couldn't be processed:
                  <ul className="mt-1 space-y-1">
                    {results.processing_errors.map((error, index) => (
                      <li key={index} className="flex items-center">
                        <span className="w-1 h-1 bg-yellow-600 rounded-full mr-2"></span>
                        <span className="font-medium">{error.filename}:</span>
                        <span className="ml-1">{error.error}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <span className="font-medium text-gray-900">Filters & Sorting</span>
          {showFilters ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </button>
        
        {showFilters && (
          <div className="px-6 pb-4 border-t border-gray-100">
            <div className="flex flex-wrap items-center gap-4 pt-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Filter by Score</label>
                <select
                  value={scoreFilter}
                  onChange={(e) => setScoreFilter(e.target.value as any)}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">All Candidates ({results.ranked_candidates.length})</option>
                  <option value="strong">Strong Match (80%+)</option>
                  <option value="good">Good Match (60-79%)</option>
                  <option value="partial">Partial Match (40-59%)</option>
                  <option value="poor">Poor Match (&lt;40%)</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
                <select
                  value={sortField}
                  onChange={(e) => handleSort(e.target.value as SortField)}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="match_score">Match Score</option>
                  <option value="skill_coverage">Skill Coverage</option>
                  <option value="matched_skills">Matched Skills</option>
                  <option value="name">Name</option>
                </select>
              </div>

              <div className="text-sm text-gray-600">
                Showing {sortedCandidates.length} of {results.ranked_candidates.length} candidates
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Results Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rank
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('name')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Candidate</span>
                    {getSortIcon('name')}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('match_score')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Match Score</span>
                    {getSortIcon('match_score')}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('skill_coverage')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Coverage</span>
                    {getSortIcon('skill_coverage')}
                  </div>
                </th>
                <th 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('matched_skills')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Skills</span>
                    {getSortIcon('matched_skills')}
                  </div>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Explanation
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sortedCandidates.map((candidate, index) => (
                <tr key={candidate.candidate_id} className="hover:bg-gray-50">
                  {/* Rank */}
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      {index < 3 ? (
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white ${
                          index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-gray-400' : 'bg-orange-600'
                        }`}>
                          {index + 1}
                        </div>
                      ) : (
                        <span className="text-gray-500">#{index + 1}</span>
                      )}
                    </div>
                  </td>

                  {/* Candidate Info */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center mr-3">
                        <User className="w-4 h-4 text-gray-600" />
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">{candidate.name}</div>
                        <div className="text-sm text-gray-500 flex items-center">
                          <Mail className="w-3 h-3 mr-1" />
                          {candidate.email}
                        </div>
                      </div>
                    </div>
                  </td>

                  {/* Match Score */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-medium text-gray-900">
                            {candidate.match_score.toFixed(1)}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              candidate.match_score >= 80 ? 'bg-green-500' :
                              candidate.match_score >= 60 ? 'bg-blue-500' :
                              candidate.match_score >= 40 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${Math.min(candidate.match_score, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                      <span className={`ml-2 px-2 py-1 text-xs font-medium rounded-full ${getMatchScoreBadgeColor(candidate.match_score)}`}>
                        {getMatchLabel(candidate.match_score)}
                      </span>
                    </div>
                  </td>

                  {/* Skill Coverage */}
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      <Target className="w-4 h-4 text-gray-400 mr-1" />
                      {candidate.skill_coverage.toFixed(1)}%
                    </div>
                  </td>

                  {/* Skills Match */}
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      <Award className="w-4 h-4 text-gray-400 mr-1" />
                      <span className="font-medium">{candidate.matched_skills}</span>
                      <span className="text-gray-500">/{candidate.total_required_skills}</span>
                    </div>
                  </td>

                  {/* Explanation */}
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900 max-w-md">
                      <div className="line-clamp-2">
                        {candidate.explanation.replace(/\*\*(.*?)\*\*/g, '$1')}
                      </div>
                    </div>
                  </td>

                  {/* Actions */}
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => setSelectedCandidate(candidate)}
                      className="text-blue-600 hover:text-blue-700 flex items-center"
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Empty State */}
        {sortedCandidates.length === 0 && (
          <div className="text-center py-12">
            <TrendingDown className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No candidates found</h3>
            <p className="text-gray-500">
              {scoreFilter !== 'all' 
                ? 'Try adjusting your filters to see more results.'
                : 'No candidates were successfully processed.'
              }
            </p>
          </div>
        )}
      </div>

      {/* Candidate Detail Modal */}
      {selectedCandidate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">{selectedCandidate.name}</h3>
                  <p className="text-gray-600">{selectedCandidate.email}</p>
                </div>
                <button
                  onClick={() => setSelectedCandidate(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <div className="p-6 space-y-6">
              {/* Match Summary */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-blue-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {selectedCandidate.match_score.toFixed(1)}%
                  </div>
                  <div className="text-sm text-blue-800">Overall Match</div>
                </div>
                <div className="bg-green-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {selectedCandidate.skill_coverage.toFixed(1)}%
                  </div>
                  <div className="text-sm text-green-800">Skill Coverage</div>
                </div>
                <div className="bg-purple-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {selectedCandidate.matched_skills}/{selectedCandidate.total_required_skills}
                  </div>
                  <div className="text-sm text-purple-800">Skills Matched</div>
                </div>
              </div>

              {/* Match Badge */}
              <div className="text-center">
                <span className={`inline-flex px-4 py-2 text-lg font-medium rounded-full ${getMatchScoreBadgeColor(selectedCandidate.match_score)}`}>
                  {getMatchLabel(selectedCandidate.match_score)}
                </span>
              </div>

              {/* Detailed Explanation */}
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-3">Match Analysis</h4>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div 
                    className="text-gray-800 leading-relaxed"
                    dangerouslySetInnerHTML={{
                      __html: selectedCandidate.explanation
                        .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>')
                        .replace(/\n/g, '<br>')
                    }}
                  />
                </div>
              </div>

              {/* Recommendation */}
              <div className="border-t pt-4">
                <div className={`rounded-lg p-4 ${
                  selectedCandidate.match_score >= 80 ? 'bg-green-50 border border-green-200' :
                  selectedCandidate.match_score >= 60 ? 'bg-blue-50 border border-blue-200' :
                  selectedCandidate.match_score >= 40 ? 'bg-yellow-50 border border-yellow-200' :
                  'bg-red-50 border border-red-200'
                }`}>
                  <h5 className={`font-semibold mb-2 ${
                    selectedCandidate.match_score >= 80 ? 'text-green-800' :
                    selectedCandidate.match_score >= 60 ? 'text-blue-800' :
                    selectedCandidate.match_score >= 40 ? 'text-yellow-800' :
                    'text-red-800'
                  }`}>
                    Recommendation:
                  </h5>
                  <p className={`text-sm ${
                    selectedCandidate.match_score >= 80 ? 'text-green-700' :
                    selectedCandidate.match_score >= 60 ? 'text-blue-700' :
                    selectedCandidate.match_score >= 40 ? 'text-yellow-700' :
                    'text-red-700'
                  }`}>
                    {selectedCandidate.match_score >= 80 
                      ? 'Highly recommended for interview. Strong alignment with job requirements.'
                      : selectedCandidate.match_score >= 60 
                      ? 'Recommended for interview. Good potential with some training or development areas.'
                      : selectedCandidate.match_score >= 40
                      ? 'Consider for interview if other candidates are limited. May require significant training.'
                      : 'Not recommended unless role requirements change or candidate gains additional experience.'
                    }
                  </p>
                </div>
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => setSelectedCandidate(null)}
                className="px-4 py-2 text-sm text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                Close
              </button>
              <button
                onClick={() => {
                  // In a real app, this would navigate to candidate profile or contact form
                  window.open(`mailto:${selectedCandidate.email}?subject=Interview Opportunity - ${results.job_info.title}`);
                }}
                className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
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