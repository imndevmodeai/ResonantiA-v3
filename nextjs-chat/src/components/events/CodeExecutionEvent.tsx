import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { VCDRichEvent } from '../../types';

interface CodeExecutionEventProps {
  event: VCDRichEvent;
}

export const CodeExecutionEvent: React.FC<CodeExecutionEventProps> = ({ event }) => {
  const codeBlock = event.code_blocks?.[0];

  if (!codeBlock) {
    return <p>No code block available for this event.</p>;
  }

  return (
    <div className="space-y-3">
      <p className="text-sm">{event.description}</p>
      <div className="bg-gray-900 rounded-md p-0">
        <SyntaxHighlighter language={codeBlock.language} style={vscDarkPlus} customStyle={{ margin: 0 }}>
          {codeBlock.code}
        </SyntaxHighlighter>
      </div>
      {codeBlock.execution_result && (
        <div>
          <h5 className="font-semibold text-gray-400">Execution Result:</h5>
          <pre className="bg-gray-900 p-2 rounded-md text-sm text-green-400 whitespace-pre-wrap">
            <code>{codeBlock.execution_result}</code>
          </pre>
        </div>
      )}
    </div>
  );
};
