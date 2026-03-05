import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Search, Plus, Loader2, BookOpen } from "lucide-react";
import { apiFetch } from "../api/client";
import type { KBArticle } from "../types";

export default function KnowledgePage() {
  const { t } = useTranslation();
  const [articles, setArticles] = useState<KBArticle[]>([]);
  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newContent, setNewContent] = useState("");
  const [newCategory, setNewCategory] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = () => {
    setLoading(true);
    setError("");
    apiFetch<{ items: KBArticle[]; total: number }>("/knowledge")
      .then((r) => setArticles(r.items))
      .catch((e) => setError(e instanceof Error ? e.message : t("common.error")))
      .finally(() => setLoading(false));
  };

  useEffect(load, [t]);

  const handleSearch = async () => {
    if (!search.trim()) return load();
    setLoading(true);
    setError("");
    try {
      const results = await apiFetch<Array<{ article_id: string; article_title: string; content: string; score: number }>>(
        "/knowledge/search",
        { method: "POST", body: JSON.stringify({ query: search }) },
      );
      setArticles(
        results.map((r) => ({
          id: r.article_id,
          title: r.article_title,
          content: r.content,
          category: null,
          is_published: true,
          created_at: "",
          updated_at: null,
        })),
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : t("common.error"));
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await apiFetch("/knowledge", {
        method: "POST",
        body: JSON.stringify({ title: newTitle, content: newContent, category: newCategory || null }),
      });
      setShowCreate(false);
      setNewTitle("");
      setNewContent("");
      setNewCategory("");
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : t("common.error"));
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t("knowledge.title")}</h1>
        <button
          onClick={() => setShowCreate(!showCreate)}
          aria-label={t("knowledge.create")}
          className="flex items-center gap-1 px-3 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg min-h-[44px]"
        >
          <Plus size={16} /> {t("knowledge.create")}
        </button>
      </div>

      {/* Search */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-3 text-zinc-500" aria-hidden="true" />
          <label className="sr-only" htmlFor="kb-search">{t("knowledge.search")}</label>
          <input
            id="kb-search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder={t("knowledge.search")}
            className="w-full pl-9 pr-3 py-2.5 bg-zinc-800 border border-zinc-700 rounded-lg text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-blue-500 min-h-[44px]"
          />
        </div>
      </div>

      {error && (
        <div className="text-center py-4 text-red-400" role="alert">{error}</div>
      )}

      {/* Create form */}
      {showCreate && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-3">
          <div>
            <label htmlFor="article-title" className="block text-xs text-zinc-400 mb-1">Title</label>
            <input
              id="article-title"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-zinc-100 placeholder-zinc-500"
            />
          </div>
          <div>
            <label htmlFor="article-content" className="block text-xs text-zinc-400 mb-1">Content</label>
            <textarea
              id="article-content"
              value={newContent}
              onChange={(e) => setNewContent(e.target.value)}
              rows={4}
              className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-zinc-100 placeholder-zinc-500"
            />
          </div>
          <div>
            <label htmlFor="article-category" className="block text-xs text-zinc-400 mb-1">Category (optional)</label>
            <input
              id="article-category"
              value={newCategory}
              onChange={(e) => setNewCategory(e.target.value)}
              className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-zinc-100 placeholder-zinc-500"
            />
          </div>
          <div className="flex gap-2">
            <button onClick={handleCreate} className="px-4 py-2.5 bg-blue-600 text-white text-sm rounded-lg min-h-[44px]">
              {t("common.save")}
            </button>
            <button onClick={() => setShowCreate(false)} className="px-4 py-2.5 bg-zinc-700 text-zinc-300 text-sm rounded-lg min-h-[44px]">
              {t("common.cancel")}
            </button>
          </div>
        </div>
      )}

      {/* Articles */}
      {loading ? (
        <div className="flex items-center justify-center h-32" role="status">
          <Loader2 className="animate-spin text-zinc-400" size={24} />
          <span className="sr-only">{t("common.loading")}</span>
        </div>
      ) : (
        <div className="space-y-2">
          {articles.map((article) => (
            <div key={article.id} className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 hover:border-zinc-700 transition-colors">
              <h3 className="font-medium text-zinc-100">{article.title}</h3>
              <p className="text-sm text-zinc-400 mt-1 line-clamp-3">{article.content}</p>
              <div className="text-xs text-zinc-600 mt-2">
                {article.category && <span className="mr-2">#{article.category}</span>}
                {article.created_at && new Date(article.created_at).toLocaleDateString()}
              </div>
            </div>
          ))}
          {articles.length === 0 && !error && (
            <div className="text-center py-12">
              <BookOpen className="mx-auto text-zinc-600 mb-2" size={32} />
              <p className="text-zinc-500">No articles found</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
