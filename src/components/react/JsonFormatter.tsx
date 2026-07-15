import { useState } from 'react';
import './JsonFormatter.css';

const SAMPLE_JSON = `{
  "name": "無限凜",
  "tools": ["json"],
  "localOnly": true,
  "count": 1
}`;

export default function JsonFormatter() {
  const [input, setInput] = useState(SAMPLE_JSON);
  const [output, setOutput] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [copyHint, setCopyHint] = useState<string | null>(null);

  function parseInput(): unknown | null {
    try {
      const parsed: unknown = JSON.parse(input);
      setError(null);
      return parsed;
    } catch (err) {
      const message = err instanceof Error ? err.message : '无效的 JSON';
      setError(message);
      setOutput('');
      setCopyHint(null);
      return null;
    }
  }

  function handleFormat() {
    const parsed = parseInput();
    if (parsed === null) return;
    setOutput(JSON.stringify(parsed, null, 2));
    setCopyHint(null);
  }

  function handleMinify() {
    const parsed = parseInput();
    if (parsed === null) return;
    setOutput(JSON.stringify(parsed));
    setCopyHint(null);
  }

  async function handleCopy() {
    if (!output) {
      setCopyHint('暂无结果可复制');
      return;
    }
    try {
      await navigator.clipboard.writeText(output);
      setCopyHint('已复制到剪贴板');
    } catch {
      setCopyHint('复制失败，请手动选择文本');
    }
  }

  return (
    <div className="json-formatter">
      <div className="json-formatter__panel">
        <label className="json-formatter__label" htmlFor="json-input">
          输入
        </label>
        <textarea
          id="json-input"
          className="json-formatter__textarea"
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            setError(null);
            setCopyHint(null);
          }}
          spellCheck={false}
          aria-invalid={error ? true : undefined}
          aria-describedby={error ? 'json-error' : undefined}
        />
      </div>

      <div className="json-formatter__actions">
        <button
          type="button"
          className="json-formatter__btn json-formatter__btn--primary"
          onClick={handleFormat}
        >
          格式化
        </button>
        <button type="button" className="json-formatter__btn" onClick={handleMinify}>
          压缩
        </button>
        <button type="button" className="json-formatter__btn" onClick={handleCopy}>
          复制结果
        </button>
      </div>

      {error ? (
        <p id="json-error" className="json-formatter__error" role="alert">
          {error}
        </p>
      ) : null}

      {copyHint ? (
        <p
          className={
            copyHint === '已复制到剪贴板'
              ? 'json-formatter__status json-formatter__status--ok'
              : 'json-formatter__status'
          }
          role="status"
        >
          {copyHint}
        </p>
      ) : null}

      <div className="json-formatter__panel">
        <label className="json-formatter__label" htmlFor="json-output">
          输出
        </label>
        <textarea
          id="json-output"
          className="json-formatter__textarea json-formatter__textarea--output"
          value={output}
          readOnly
          spellCheck={false}
          placeholder="格式化或压缩后的结果会显示在这里"
        />
      </div>
    </div>
  );
}
