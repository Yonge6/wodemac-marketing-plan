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
- `materials.json`：素材清单。已上架一张学生家长参考截图，可下载原图；其余素材仍为占位。
- `materials.js`：分类筛选及图片、下载状态展示。

后续上传海报到仓库（建议放入 `assets/materials/`），将清单对应条目的 `image` 改为图片相对路径即可上架。`download` 可选，留空时下载原图。建议海报比例为 iPhone 竖版 1170 × 2532；所有占位图和预览均使用相同比例。

## 访问地址

- 正式地址：https://wodemac.vilesaint.com/
- 宣传素材：https://wodemac.vilesaint.com/materials.html

## 客户案例

- `cases.html` / `cases.json`：按四类客户筛选，当前每类两个照片占位，尚无真实案例。
- 将客户照片放入 `assets/cases/`，填写对应条目的 `image`、`title` 和 `description` 即可上架；`download` 留空时下载原图。
- 与宣传素材共用 `materials.js`；支持 `#training`、`#business`、`#parents` 和 `#service` 分类直达。
- 客户案例：https://wodemac.vilesaint.com/cases.html

## 年付批量折扣

年付批量折扣采用最新提供的阶梯：同一账户同时在租 1–3 台原价、4–10 台 95 折、11–25 台 93 折、26–50 台 9 折、51–100 台 85 折；100 台以上单独报价，下限 8 折。以 $1,723.80 为单台年付基准，先将折后单台年费保留两位，再计算测算总额。销售目标与同一账户台数分别计算。

## 微信联系

营销方案底部 `#contact` 展示 Elian 微信二维码，原图来自官网 `https://wodemac.com/assets/wechat-qr.jpg`，保存在 `assets/contact/elian-wechat-qr.jpg`。页面支持查看与保存原图；如二维码更新，请同步替换此文件。
- 域名解析：`wodemac` CNAME → `yonge6.github.io`；GitHub Pages 自定义域名由根目录 `CNAME` 保留。
