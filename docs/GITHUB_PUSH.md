# GitHub 上传说明

本地已按里程碑完成 **4 次 commit**，远程尚未推送（需先登录 GitHub）。

## 本地提交历史

```
1aa5aaa feat: add HTML slide export and PyQt6 GUI (P1 MVP)
d9d67da feat: batch import 96 NCE2 lessons to JSON
125edee feat: add nce2_core parsing pipeline
054c9b2 chore: scaffold nce2_sentence_components project
```

## 一次性上传（推荐）

1. 在 GitHub 网页创建空仓库：`39976148/nce2_sentence_components`（不要勾选 README）
2. 登录 GitHub CLI：
   ```powershell
   gh auth login
   ```
3. 推送：
   ```powershell
   cd D:\cursor_work\nce2_sentence_components
   git push -u origin main
   ```

## 或使用 gh 创建仓库并推送

```powershell
cd D:\cursor_work\nce2_sentence_components
gh auth login
gh repo create nce2_sentence_components --public --source=. --remote=origin --push
```

## 分阶段推送（可选）

若希望模拟「按进度上传」，可在另一台已联网机器上：

```powershell
git push origin 054c9b2:main
git push origin 125edee:main
git push origin d9d67da:main
git push origin 1aa5aaa:main
```

## 网络问题

若出现 `Connection was reset`，请检查代理/VPN，或改用 SSH：

```powershell
git remote set-url origin git@github.com:39976148/nce2_sentence_components.git
git push -u origin main
```
