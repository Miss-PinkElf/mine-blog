/** 工具清单 — tools 列表页与主站入口共用 */

export type ToolMeta = {
  slug: string;
  title: string;
  description: string;
};

export const tools: readonly ToolMeta[] = [
  {
    slug: 'json',
    title: 'JSON 格式化',
    description: '格式化、压缩与语法校验，数据仅在浏览器内处理',
  },
] as const;
