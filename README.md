生体ボリュームイメージング研究会のためにアレンジした、サンプルEM連続断層画像、サンプル教師セグメンテーション画像、FFN-Windows10(64bit)版、前処理、後処理などのアクセサリプログラムをアップロードしました。

http://www.sssem.info/registration-18-3.html

ここでは、ATUM/SEMによって連続断層撮影されたMouse somatosensory cortexの細胞膜のセグメンテーションを行います。撮影データは ISBI 2013 challenge ([SNEMI3D](http://brainiac2.mit.edu/SNEMI3D/)) において用いられたものをそもまま使用させて頂いております。EM画像には、使用前に Contrast Limited Adaptive Histogram Equalization (CLAHE)フィルタを通しています (blocksize 127,　Histogram bins 256, max slope 1.50) 。同データを用いた論文は Kasthuri et al. ( Cell 162(3):648-61, 2015 ) に出版されました。EM画像は Open Data Commons Attribution License (ODC-By) v1.0 ライセンスのもと公開されています。

#### 必要条件
-	ハイパフォーマンスデスクトップPC（30万円～）
	- OS：Windows 10 [Linux の場合は、オリジナルのプログラム https://github.com/google/ffn を用いてください。]
	- GPU:NVIDIA GTX1080ti以上

-	Python3.6をインストールしてください。
		Cuda9.0, Cudnn7.Xをインストールしてください。

	- (参考) cuda 9.0, cuDNN v7のインストール方法。
		- https://qiita.com/spiderx_jp/items/8d863b087507cd4a56b0
		- https://qiita.com/kattoyoshi/items/494238793824f25fa489
		- https://haitenaipants.hatenablog.com/entry/2018/07/25/002118


#### EM画像と教師セグメンテーションの確認

```EM画像と教師セグメンテーションの確認
> dir [ffn_windows]\preprocessing\images
	0000.png
	0001.png
	...
	0099.png

> dir [ffn_windows]\preprocessing\segment
	0000.png
	0001.png
	...
	0099.png
```

	EM画像は [ffn_windows]/preprocessing/images フォルダに 8ビット gray-scale png にて、教師セグメンテーションは	
	[ffn_windows]/preprocessing/segment フォルダに 16bit gray-scale png にて保存されていることを確認してください。

#### hdf5 containerファイル生成

```hdf5 containerファイル生成
> cd [ffn_windows]\preprocessing\images
> python png_to_h5.py images.h5
> python png_mean_std.py
    Mean:  131
    Std :  62

> cd [ffn_windows]\preprocessing\segment
> python png_to_h5.py ground_truth.h5

> copy [ffn_windows]\preprocessing\images\images.h5  [ffn_windows]\ffn\preprocessed_files\
> copy [ffn_windows]\preprocessing\segment\ground_truth.h5  [ffn_windows]\ffn\preprocessed_files\
```
	png連続ファイルがhdf5コンテナ形式に変換されて保存されます。また、EM画像については、
	png_mean_std.pyを用いて画像の平均強度と標準偏差を求めて記録してください。

#### af.h5中間ファイル生成

```af.h5中間ファイル生成
> cd [ffn_windows]\ffn
> python  compute_partitions.py ^
    --input_volume  preprocessed_files\ground_truth.h5@raw ^
    --output_volume  preprocessed_files\af.h5@af ^
    --thresholds  0.025,0.05,0.075,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9 ^
    --lom_radius  24,24,24 ^
    --min_size  10000
```
	5-30分程度かかります。

#### tf_record_file中間ファイル生成

```tf_record_file中間ファイル生成
> cd [ffn_windows]\ffn
> python  build_coordinates.py ^
     --partition_volumes validation1@preprocessed_files\af.h5@af ^
     --coordinate_output preprocessed_files\tf_record_file ^
     --margin 24,24,24
```
	5-30分程度かかります。hdf5中間ファイルは [ffn_windows]\ffn\preprocessed_files に作成されたものが入っていますが
	本ファイルはファイルサイズが大きいため、未作成です。必ず作成してください。

#### トレーニング実行

```トレーニング実行
> cd [ffn_windows]\ffn
> mkdir training_results
> python train.py ^
    --train_coords  preprocessed_files\tf_record_file ^
    --data_volumes  validation1@preprocessed_files\images.h5@raw ^
    --label_volumes  validation1@preprocessed_files\ground_truth.h5@raw ^
    --model_name  convstack_3d.ConvStack3DFFNModel ^
    --model_args  "{\"depth\":9,\"fov_size\":[33,33,17],\"deltas\":[8,8,4]}" ^
    --image_mean  131 ^
    --image_stddev  62 ^
    --train_dir  training_results ^
    --max_steps  1000000
```
	image_mean, image_stddevにEM画像の平均強度、標準偏差を記入してください。max_stepsに最大ステップ数を記入してください。
	推論に用いるためには数百万回以上のトレーニングが必要です。私達の経験では、NVIDIA社の高性能GPUを搭載したPCで 
	最低3日、標準的には2-3週間かかります。


#### 推論実行

```推論実行
> python run_inference_win.py ^
	--image_size_x 256 ^
	--image_size_y 256 ^
	--image_size_z 100 ^
	--parameter_file configs/inference.pbtxt
```

	推論結果（セグメンテーション）が numpy形式にて [ffn_windows]/ffn/inference_results/0/0/seg-0_0_0.npz,
	[ffn_windows]/ffn/inference_results/0/0/seg-0_0_0.prob に保存されます。
	NVIDIA社の高性能GPUを搭載したPCで数十分かかります。
	サンプルとして添付した256x256 xy-pixels,　100 z-sliceのファイルの推論は5分程度です。
	前回の推論結果seg-0_0_0.npz, seg-0_0_0.probが残っていると推論が実行されません。実行前に消してください。

#### 推論結果の png 形式への変更

```推論結果の png 形式への変更
> copy [ffn_windows]\ffn\inference_results\0\0\seg-0_0_0.npz  [ffn_windows]\postprocessing\
> cd [ffn_windows]\postprocessing
> python npz_png.py
```

	推論結果（セグメンテーション）が png形式にて [ffn_windows]/postprocessing に
	0000.png, 0001.png, ...., 0099.pngと保存されます。

#### 宣伝
Windows10, 64bitにおいてGUIを用いてFFNを行い、校正・視覚化を行うこともできるソフトウェアを開発しました。是非、お試しください！
- https://github.com/urakubo/Dojo-standalone

#### 連絡先
- 浦久保　秀俊
- urakubo-h [アット] sys.i.kyoto-u.ac.jp
- https://researchmap.jp/urakubo/

