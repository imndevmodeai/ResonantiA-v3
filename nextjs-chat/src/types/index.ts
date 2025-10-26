export interface VCDRichEvent {
  event_id: string;
  event_type: 'analysis_start' | 'phase_start' | 'web_search' | 'web_browse' | 'code_execution' | 'simulation_run' | 'data_visualization' | 'strategy_synthesis' | 'thought_process' | 'phase_complete' | 'analysis_complete' | 'system_message';
  timestamp: string;
  phase: string;
  title: string;
  description: string;
  
  links?: { url: string; title: string; description: string; clickable: boolean }[];
  code_blocks?: { code: string; language: string; execution_result?: string; interactive?: boolean }[];
  simulations?: any[];
  visualizations?: any[];
  
  expandable?: boolean;
  drill_down_enabled?: boolean;
  interactive?: boolean;
  
  metadata?: Record<string, any>;
  tags?: string[];
}




