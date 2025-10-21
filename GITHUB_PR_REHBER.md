# GitHub Pull Request Nasıl Oluşturulur? - Görsel Rehber

## 1. ADIM: Repository Ana Sayfası

```
GitHub Ana Sayfa
┌────────────────────────────────────────────────────────────┐
│  MuhammedEbrar / RandevuRezervasyonSistemi                  │
├────────────────────────────────────────────────────────────┤
│  [Code]  [Issues]  [Pull requests]  [Actions]  [Projects]  │  ← BURAYA TIKLA
├────────────────────────────────────────────────────────────┤
│                                                             │
│  main branch                                                │
│  About                                                      │
└────────────────────────────────────────────────────────────┘
```

## 2. ADIM: Pull Requests Sayfası

```
Pull Requests
┌────────────────────────────────────────────────────────────┐
│  [New pull request]  ← BU YEŞİL BUTONA TIKLA              │
├────────────────────────────────────────────────────────────┤
│  Filters ▼                                                  │
│                                                             │
│  No open pull requests                                      │
└────────────────────────────────────────────────────────────┘
```

## 3. ADIM: Compare Changes

```
Comparing Changes
┌────────────────────────────────────────────────────────────┐
│  base: [dev ▼]  ←  compare: [claude/fix-security... ▼]    │
│                                                             │
│  ✓ Able to merge. These branches can be automatically      │
│    merged.                                                  │
│                                                             │
│  [Create pull request]  ← BU YEŞİL BUTONA TIKLA           │
├────────────────────────────────────────────────────────────┤
│  Showing 10 changed files with 57 additions and 62...       │
└────────────────────────────────────────────────────────────┘
```

## 4. ADIM: Open Pull Request

```
Open a pull request
┌────────────────────────────────────────────────────────────┐
│  security: Fix critical security vulnerabilities and bugs  │
│  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔  │
│                                                             │
│  Write   Preview                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ ## Yapılan Değişiklikler                            │  │
│  │                                                      │  │
│  │ ✅ AWS private key kaldırıldı                       │  │
│  │ ✅ Database credentials kaldırıldı                  │  │
│  │ ✅ 4 kritik bug düzeltildi                          │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  [Create pull request]  ← BU YEŞİL BUTONA TIKLA           │
└────────────────────────────────────────────────────────────┘
```

## 5. ADIM: Merge Pull Request

```
Pull Request #X
┌────────────────────────────────────────────────────────────┐
│  security: Fix critical security vulnerabilities and bugs  │
│  Open    MuhammedEbrar wants to merge 1 commit into dev    │
├────────────────────────────────────────────────────────────┤
│  Conversation   Commits (1)   Files changed (10)           │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ✓ This branch has no conflicts with the base branch       │
│                                                             │
│  [Merge pull request]  ← BU YEŞİL BUTONA TIKLA            │
│                                                             │
│  Merge method: [Create a merge commit ▼]                   │
└────────────────────────────────────────────────────────────┘
```

## 6. ADIM: Confirm Merge

```
┌────────────────────────────────────────────────────────────┐
│  Merge pull request #X from claude/fix-security...         │
│  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔  │
│                                                             │
│  [Confirm merge]  ← BU YEŞİL BUTONA TIKLA                 │
│  [Cancel]                                                   │
└────────────────────────────────────────────────────────────┘
```

## 7. ADIM: BAŞARILI! 🎉

```
┌────────────────────────────────────────────────────────────┐
│  ✓ Pull request successfully merged and closed             │
│                                                             │
│  You're all set—the claude/fix-security... branch can be   │
│  safely deleted.                                            │
│                                                             │
│  [Delete branch]  ← İsterseniz branch'i silebilirsiniz     │
└────────────────────────────────────────────────────────────┘
```

---

## ÖZET

1. **Pull requests** sekmesi
2. **New pull request** butonu
3. **base: dev**, **compare: claude/fix-security...**
4. **Create pull request** (2 kez tıkla)
5. **Merge pull request** → **Confirm merge**
6. Bitti! ✅

