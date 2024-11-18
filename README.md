# 运行方式
```bash
conda create -n head_detection_onnx python=3.10.12
conda activate head_detection_onnx
pip install -r requirements.txt
python main.py
```

# 代码
- https://github.com/AbelKidaneHaile/Reports
  - 基于YOLOv8，应该可以训练。
  - 本项目基于此代码。
- https://github.com/Varat7v2/Human-Head-Detection
  - 没有训练代码。
- https://github.com/aditya-vora/FCHD-Fully-Convolutional-Head-Detector
  - 训练代码和测试代码都比较完善。
  - 代码还提供了演示视频，确认可以检测后脑勺。
  - star 数为 647。
  - 时间为2018年。

# 论文
- https://arxiv.org/pdf/1809.08766

# 数据集
- Brainwash Dataset
  - https://www.di.ens.fr/willow/research/headdetection/
- HollywoodHeads Dataset
- SCUT-HEAD
  - https://github.com/HCIILAB/SCUT-HEAD-Dataset-Release