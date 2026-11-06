# wodeMac 营销方案

原始 HTML 的 GitHub Pages 静态发布版本，保留营销方案和目标调整功能；已移除算账页面。

- 来源：用户提供的 `wodeMac 营销方案.html`（2026-11-05 版）
- 发布：GitHub Pages，`main` 分支根目录
- 无需构建或安装依赖
- GitHub Pages 不连接 Claude 数据库；目标修改通过浏览器 localStorage 保存在各自设备
- 页面中的价格、目标和财务假设均来自原文件，发布不代表重新核验

更新 `index.html` 并推送后，GitHub Pages 会自动重新发布。

## 页面与素材维护

- `index.html`：营销方案、章节导航及 10 / 20 / 50 / 100 / 200 / 500 台目标切换。
- `styles.css`：方案与素材中心共享样式，包含手机排版及打印样式。
- `materials.html`：宣传素材中心，按四类客户筛选。
- `materials.json`：素材清单。当前图片均为占位，未提供真实下载。
- `materials.js`：分类筛选及图片、下载状态展示。

后续上传海报到仓库（建议放入 `assets/materials/`），将清单对应条目的 `image` 改为图片相对路径即可上架。`download` 可选，留空时下载原图。建议海报比例为 iPhone 竖版 1170 × 2532；所有占位图和预览均使用相同比例。

## 访问地址

- 正式地址：https://wodemac.vilesaint.com/
- 宣传素材：https://wodemac.vilesaint.com/materials.html
- 域名解析：`wodemac` CNAME → `yonge6.github.io`；GitHub Pages 自定义域名由根目录 `CNAME` 保留。
