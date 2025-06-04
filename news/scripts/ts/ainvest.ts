// 通过puppeteer爬取网页数据
import puppeteer from 'puppeteer';
import { historyPosts } from './util';
import { writeFileSync } from 'fs';

const filepath = './data/ainvest/list.json';

async function fetchNews() {
    let insert = false;
    const historyPostsData = historyPosts(filepath);
    let articles = historyPostsData.articles;
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    await page.goto(`https://www.ainvest.com/news/`);
    await new Promise(resolve => setTimeout(resolve, 7000));

    // Extract data
    const data = await page.evaluate(() => {
        const elements = document.querySelectorAll('.article-main > .article-item');
        // 遍历 elements
        const result = [];
        for (let i = 0; i < 2; i++) {
            const element = elements[i];
            let post = {
                link: element.getAttribute('datasrc') || "",
                image: element.querySelector('.img-box > img')?.getAttribute('src') || "",
                title: element.querySelector('.article-title')?.textContent?.trim() || "",
                author: element.querySelector('.account-name')?.textContent?.trim() || "",
                description: ""
            }
            // 使用historyPosts函数获取历史文章判定是否已爬取
            if (historyPostsData.links.includes(post.link)) {
                break;
            }else{
                result.unshift(post);
            }
        }
        return result;
    });

    for (let i = 0; i < data.length; i++) {
        const postLink = data[i].link;
        if (postLink) {
            await page.goto(postLink);
            await new Promise(resolve => setTimeout(resolve, 7000));
            data[i].description = await page.evaluate(() => {
                return document.querySelector('.news-content')?.outerHTML?.trim() || "";
            });
            if (data[i].description) {
                insert = true
                articles.unshift(data[i]);
            }
        }
    }

    if (articles.length > 0 && insert) {
        articles = articles.slice(0, 10);
        // 覆盖式写入 filepath
        writeFileSync(filepath, JSON.stringify({ data: articles }));
        console.log("ainvest news fetch success");
    }

    console.log(data);
    await browser.close();
}

fetchNews();