# PKGF 公理系（Axiomatic Formulation）  
**DOI: [10.5281/zenodo.19344285](https://doi.org/10.5281/zenodo.19344285)**

以下、すべての対象は滑らかな有限次元多様体 \(M\) 上で定義されるものとする。

---

# **1. 基本対象**

- **多様体:** 滑らかな有限次元多様体 \(M\)  
- **接束:** \(TM\)

---

# **2. 公理**

---

## **公理 P1（分解構造）**

\[
TM = \bigoplus_{\alpha \in I} E_\alpha.
\]

---

## **公理 P2（内部自己同型場）**

\[
K \in \Gamma(\mathrm{End}(TM)).
\]

---

## **公理 P3（ゲージ群）**

\[
\mathcal{G} \subset \Gamma(\mathrm{GL}(TM))
\]

任意の \(H \in \mathcal{G}\) は：

1. \[
   K \mapsto H K H^{-1}
   \]
2. \[
   H(E_\alpha) = E_\alpha
   \]

を満たす。

---

## **公理 P4（外部接続）**

接束上に滑らかな接続 \(\nabla\) が存在する。

**局所フレームに関する接続 1-形式を \(\omega\)** とするとき：

\[
F = d\omega + \omega \wedge \omega.
\]

さらに本理論では：

\[
\nabla : \Gamma(TM) \to \Gamma(T^*M \otimes TM)
\]

を **一次微分作用素として基本対象とし**、そのゲージ変換を

\[
\nabla' = H \circ \nabla \circ H^{-1}
\quad (\Gamma(TM)\text{ 上の作用として})
\]

により定義する。

---

## **公理 P5（結合方程式）**

内部ゲージ 1-形式：

\[
\Omega \in \Omega^1(M, \mathrm{End}(TM))
\]

に対し：

\[
\nabla K = [\Omega, K].
\]

ここで \(\Omega\) は **随伴変換に従う End(TM)-値 1-形式（テンソル）** とする。

**さらに \(\nabla K\) は、接続 \(\nabla\) により誘導される  
\(\mathrm{End}(TM)\) 上の共変微分を意味する。**

---

## **公理 P6（完全ゲージ共変性）**

任意の \(H \in \mathcal{G}\) に対し：

- \[
  K \mapsto H K H^{-1}
  \]

- \[
  \omega \mapsto H \omega H^{-1} + H dH^{-1}
  \]

- \[
  \Omega \mapsto H \Omega H^{-1}
  \]

- \[
  \nabla' = H \circ \nabla \circ H^{-1}
  \quad (\Gamma(TM)\text{ 上の作用として})
  \]

このとき：

\[
\nabla' K' = [\Omega', K']
\]

が成り立ち、結合方程式は完全に形式不変である。

---

## **公理 P7（情報結合）**

\[
s = \psi(\Phi)
\]

内部ゲージ 1-形式は：

\[
\Omega = \Omega(s(x), x).
\]

---

# **4. 定義（PKGF構造）**

公理 **P1–P7** を満たすデータ：

\[
(M,\{E_\alpha\}, K, \mathcal{G}, \nabla, \Omega, \Phi)
\]

を **PKGF構造（PKGF structure）** と呼ぶ。

---

# **5. 定理**

---

## **定理 1（共役不変量）**

\[
\det(K), \quad \mathrm{Spec}(K)
\]

はゲージ群の作用の下で不変。

---

## **定理 2（共変性の保存）**

\[
\nabla K = [\Omega, K]
\]

はゲージ変換に対し：

\[
\nabla' K' = [\Omega', K']
\]

として形式不変。

---

## **定理 3（分解保存）**

\[
[K, \Pi_\alpha] = 0
\quad \Rightarrow \quad
K(E_\alpha) \subset E_\alpha.
\]

---

## **定理 4（曲率の変換）**

\[
\omega \mapsto H \omega H^{-1} + H dH^{-1}
\quad \Rightarrow \quad
F \mapsto H F H^{-1}.
\]

---

# **6. 備考（整合性について）**

本体系では：

- \(\nabla\) を **作用素として公理化**し  
- \(\omega\) はその局所表現とみなし  
- \(\Omega\) は随伴テンソルとして扱う  

ことで、結合方程式のゲージ共変性が **厳密に成立**する。

---
