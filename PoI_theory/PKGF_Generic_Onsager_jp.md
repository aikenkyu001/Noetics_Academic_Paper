# **Parallel Key Geometric Flow におけるエネルギー構造と GENERIC / Onsager 形式との比較解析**

**著者：Fumio Miyata**  
**日付：2026年4月**
**DOI:** [https://doi.org/10.5281/zenodo.20018571](https://doi.org/10.5281/zenodo.20018571)  
**Repository:** [https://github.com/aikenkyu001/PoI_theory](https://github.com/aikenkyu001/PoI_theory)  

**関連文献**：  
*Parallel Key Geometric Flow (PKGF): A Mathematical Infrastructure for Unified Conservative–Dissipative Systems*  
*Spectral Flow in the Unified Phase of the Parallel Key Geometric Flow*

---

## **要旨（Abstract）**

本稿では、Parallel Key Geometric Flow（PKGF）における **エネルギー構造**を解析し、  
非平衡熱力学の代表的枠組みである **GENERIC（General Equation for Non-Equilibrium Reversible–Irreversible Coupling）** および  
**Onsager の線形応答理論**との比較を行う。

PKGF は保存的成分（交換子型）と散逸的成分（楕円型作用素）を複素化によって統合する線形作用素流であり、  
そのエネルギー減衰構造は GENERIC や Onsager の散逸構造と類似点を持つ一方で、  
エネルギー・エントロピーの分離や degeneracy 条件の扱いにおいて重要な相違点が存在する。

本稿の目的は、PKGF が既存の非平衡理論とどのように整合し、どこに差異があるのかを  
**数学的に慎重かつ誠実に整理すること**であり、  
GENERIC や Onsager の理論に新たな結果を加えることではない。

---

# **1. 序論**

Parallel Key Geometric Flow（PKGF）は、  
- 保存的成分：\([\Omega, K]\)  
- 散逸的成分：\(\mathcal{D}(K)\)  
を複素化によって統合する作用素進化方程式である。知能を保存則と metriplectic 流に基づく物理的プロセスとして捉える視点は、近年の知能の物理理論とも深く共鳴している [Fagan 2026]。

PKGF の特徴は、扱う変数が **状態そのものではなく、状態を生成・変換する構造（作用素）** である点にある。  
これは GENERIC や Onsager が扱う「マクロ状態変数」とは階層が異なる。

本稿では、PKGF のエネルギー構造を GENERIC / Onsager と比較し、  
類似点と相違点を明確化する。

---

# **2. PKGF のエネルギー構造**

PKGF の散逸項は

\[
\mathcal{D}(K) = -\nabla^*\nabla K - (V K + K V), \qquad V(x) \ge cI > 0
\]

で与えられ、全体の進化は

\[
\partial_t K = [\Omega, K] + \lambda \mathcal{D}(K), \qquad \lambda > 0
\]

である。

---

## **2.1 エネルギー汎関数**

本稿で用いるエネルギー汎関数

\[
E(K) = \frac{1}{2}\langle\!\langle K, K\rangle\!\rangle_{L^2}
\]

は、物理学における内部エネルギーそのものではなく、  
**作用素 \(K\) が持つ構造的な振幅（あるいは二乗可積分ノルム）**  
を測る量である。

したがって、PKGF におけるエネルギー減衰は、  
熱力学的エネルギーの散逸というよりは、  
**構造の単純化・抽象化・忘却（Noetics の D-phase）**  
に対応する。

散逸項 \(\mathcal{D}\) は負定値作用素として定義されており、  
\[
\frac{d}{dt}E(K(t)) = \langle\!\langle \mathcal{D}(K), K\rangle\!\rangle_{L^2} \le 0
\]
が成立する。このエネルギー安定性は、Onsager の原理に基づいた構造保存スキームの解析手法によって数学的に正当化される [Chen et al. 2024]。

---

# **3. GENERIC との比較**

GENERIC の基本構造 [Grmela 2025]：

\[
\dot{x} = L(x)\nabla E(x) + M(x)\nabla S(x)
\]

ここで  
- \(L\)：Poisson 構造（反対称）  
- \(M\)：散逸作用素（対称・正定値）  
- **degeneracy 条件**  
  \[
  L\nabla S = 0,\quad M\nabla E = 0
  \]

---

## **3.1 類似点**

| GENERIC | PKGF |
|--------|-------|
| 可逆項 \(L\nabla E\) | 交換子項 \([\Omega, K]\) |
| 散逸項 \(M\nabla S\) | 楕円型散逸項 \(\mathcal{D}(K)\) |
| エネルギー減衰 | \(\frac{d}{dt}E(K)\le 0\) |

- 可逆・不可逆の二重構造  
- 散逸項が gradient-like  
- 保存項がエネルギーに寄与しない  

という点で構造的類似性がある。

---

## **3.2 相違点**

### **(1) 変数の階層性の違い（重要）**

- GENERIC の \(x\)：密度・運動量・温度などの **マクロ状態変数**  
- PKGF の \(K\)：Hilbert 束上の **作用素（構造そのもの）**

PKGF は **状態のダイナミクスではなく、構造のダイナミクス** を扱うため、  
Poisson 構造ではなく **Lie 代数的交換子構造** が自然に現れる。

### **(2) Poisson 構造 vs Lie 代数構造**

GENERIC の Poisson 構造は symplectic 幾何に基づくが、  
PKGF の交換子構造は作用素代数に基づく。

### **(3) エネルギー・エントロピーの分離の不在**

GENERIC では \(E\) と \(S\) が明確に分離されるが、  
PKGF の \(E(K)\) は構造ノルムであり、  
エントロピー生成との直接対応はない。

### **(4) degeneracy 条件の不成立**

GENERIC の  
\[
M\nabla E = 0
\]
はエネルギー保存を保証するが、  
PKGF では一般に成立しない。

これは PKGF において、  
**構造の散逸がそのままエネルギー減少に結びつく**  
という Noetics 的特徴を反映している。

### **(5) 無限次元性**

PKGF は Hilbert 束上の無限次元作用素流であり、  
GENERIC の有限次元形式とは解析的性質が異なる。

---

# **4. Onsager 形式との比較**

Onsager の線形応答理論：

\[
\dot{x} = -Lx
\]

ここで \(L\) は対称・正定値。近年の研究では、深層学習における散逸方程式を Onsager の原理から導出する試みもなされている [Chang et al. 2025]。

---

## **4.1 類似点**

- PKGF の散逸項 \(\mathcal{D}\) は線形であり、Onsager の線形散逸と対応  
- 強楕円性により正則化効果がある  

---

## **4.2 相違点**

Onsager reciprocity（線形応答の対称性）は、  
PKGF の散逸項 \(\mathcal{D}\) では一般に成立しない [Fuchs et al. 2018]。

しかしこれは欠点ではなく、  
**非対称なフィードバック構造を持つ知能システム**  
（例：制御系、学習系、回路）では reciprocity が破れるのが自然であり、  
PKGF の散逸構造はむしろその特徴を正確に反映している。

---

# **5. PKGF の位置づけ**

以上の比較から、PKGF は：

- GENERIC の「包含」でも「拡張」でもなく、  
- Onsager の「一般化」でもなく、  

**可逆・不可逆の二重構造を持つ作用素流を扱うための、  
独立した数学的枠組み**である。

PKGF のエネルギー構造は GENERIC / Onsager と整合する部分を持つが、  
degeneracy 条件やエントロピー構造の扱いにおいて本質的に異なる。

---

# **6. 結論**

本稿では、PKGF のエネルギー構造を GENERIC および Onsager 形式と比較し、  
類似点と相違点を数学的に整理した。

- 可逆・不可逆の二重構造  
- 散逸項によるエネルギー減衰  
- 保存項のエネルギー不変性  

といった構造的類似性がある一方で、

- 変数の階層性の違い  
- Poisson 構造の欠如  
- エネルギー・エントロピーの分離の不在  
- degeneracy 条件の不成立  

など、重要な相違点が存在する。

PKGF は非平衡熱力学の既存理論を置き換えるものではなく、  
**作用素論的・幾何学的観点から非平衡ダイナミクスを扱うための  
独立した枠組み**として位置づけられる。

---

# **参考文献**

[Chang 2025] Chang, Z., Wen, Z., & Zhao, X. (2025). Unsupervised operator learning approach for dissipative equations via Onsager principle.  
[Chen 2024] Chen, H., Liu, H., & Xu, X. (2024). The Onsager principle and structure preserving numerical schemes.  
[Fagan 2026] Fagan, P. D. (2026). Toward a Physical Theory of Intelligence.  
[Fuchs 2018] Fuchs, J. N., Piéchon, F., & Montambaux, G. (2018). Landau levels, response functions and magnetic oscillations from a generalized Onsager relation.  
[Grmela 2025] Grmela, M. (2025). Rheological modeling with GENERIC and with the Onsager principle.  
[Palffy-Muhoray 2017] Palffy-Muhoray, P., Virga, E. G., & Zheng, X. (2017). Onsager's missing steps retraced.  
