export type Confidence = "high" | "medium" | "low";

export type EntryPointDetail = {
  path: string;
  reason: string;
  source: string;
};

export type FileImports = {
  internal: string[];
  external: string[];
};

export type FrequentPackage = {
  package: string;
  count: number;
};

export type ImportsBlock = {
  by_file: Record<string, FileImports>;
  frequent_packages: FrequentPackage[];
};

export type ApiEndpoint = {
  method: string;
  path: string;
  file: string;
  line: number;
  framework: string;
};

export type DependencyEdge = {
  source: string;
  target: string;
};

export type RepositoryHealth = {
  readme_present: boolean;
  license_present: boolean;
  tests_detected: boolean;
  docker_detected: boolean;
  ci_workflow_detected: boolean;
  github_actions_detected: boolean;
  env_example_detected: boolean;
  package_managers: string[];
};

export type CodeSymbol = {
  name: string;
  file: string;
  line: number;
};

export type LargestFile = {
  path: string;
  lines: number;
  bytes: number;
};

export type FileWithMostImports = {
  path: string;
  import_count: number;
  internal_count?: number;
  external_count?: number;
};

export type CodeAnalysis = {
  python_files_analyzed: number;
  javascript_files_analyzed: number;
  classes: CodeSymbol[];
  functions: CodeSymbol[];
  largest_files: LargestFile[];
  files_with_most_imports: FileWithMostImports[];
};

export type RepositoryIntelligence = {
  name: string;
  files: number;
  directories: number;
  has_readme: boolean;
  readme_preview: string;
  important_files: string[];
  technologies: string[];
  entry_points: string[];
  entry_point_details: EntryPointDetail[];
  imports: ImportsBlock;
  api_endpoints: ApiEndpoint[];
  dependency_map: DependencyEdge[];
  repository_health: RepositoryHealth;
  code_analysis: CodeAnalysis;
  project_structure: string;
  top_level_folders: string[];
  project_purpose: string;
};

export type RepositoryNavigation = {
  start_here: string;
  execution_flow: string[];
  important_dependencies: string[];
};

export type UnderstandFirst = {
  concept: string;
  reason: string;
};

export type OpenTheseFile = {
  path: string;
  reason: string;
  confidence: Confidence;
};

export type ArchitectureWalkthroughStep = {
  step: number;
  description: string;
  evidence: string;
};

export type RampUpBrief = {
  repository_snapshot: string;
  repository_navigation: RepositoryNavigation;
  understand_first: UnderstandFirst[];
  open_these_files: OpenTheseFile[];
  architecture_walkthrough: ArchitectureWalkthroughStep[];
  implementation_plan: string[];
  potential_risks: string[];
  estimated_difficulty: string;
  estimated_time_to_first_contribution: string;
};

export type AnalyzeResponse = {
  github_url: string;
  role: string;
  mission: string;
  repository: RepositoryIntelligence;
  rampup_brief: RampUpBrief | null;
};

export type AnalyzeRequest = {
  github_url: string;
  role: string;
  mission: string;
};
