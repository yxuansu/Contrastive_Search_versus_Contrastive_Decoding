# An Empirical Comparison Between Contrastive Search And Contrastive Decoding For Open-ended Text Generation
**Authors**: Yixuan Su and Jialu Xu


****

<span id='all_catelogue'/>

### Catalogue:
* <a href='#introduction'>1. Introduction</a>
* <a href='#environment_setup'>2. Environment Setup</a>

****

<span id='introduction'/>

#### 1. Introduction: <a href='#all_catelogue'>[Back to Top]</a>

****

<span id='environment_setup'/>

#### 2. Environment Setup: <a href='#all_catelogue'>[Back to Top]</a>
Before running the experiments, please setup the environment as
```yaml
pip install torch
pip install simctg --upgrade
pip install "transformers>=4.24.0"
```


```
========================================== Domain: Wikinews ==========================================
Contrastive Search is better at 68.5%; Two methods are comparable at 2.0%; Contrastive Decoding is better at 29.5%
------------------------------------------------------------------------------------------------------

========================================== Domain: Wikitext ==========================================
Contrastive Search is better at 65.0%; Two methods are comparable at 2.0%; Contrastive Decoding is better at 33.0%
------------------------------------------------------------------------------------------------------

========================================== Domain: Story ==========================================
Contrastive Search is better at 67.0%; Two methods are comparable at 1.0%; Contrastive Decoding is better at 32.0%
------------------------------------------------------------------------------------------------------
```
