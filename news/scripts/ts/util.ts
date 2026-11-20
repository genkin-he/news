import { readFileSync } from 'fs';

interface Article {
    link: string;
}

interface HistoryPostsResult {
    articles: Article[];
    links: string[];
}

export function historyPosts(filepath: string): HistoryPostsResult {
    try {
        const data = readFileSync(filepath, 'utf-8');
        const articles: Article[] = JSON.parse(data).data;
        const links: string[] = articles.map(article => article.link);
        return { articles, links };
    } catch (error) {
        return { articles: [], links: [] };
    }
}
