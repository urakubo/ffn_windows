
生体ボリュームイメージング研究会のために作成した、Windows10, 64bitにてffnを実行するためのプログラムです。

http://www.sssem.info/registration-18-3.html


cd [ffn_windows]/preprocessing/image
python png_to_h5.py image.h5
python png_mean_std.py
Mean:  131
Std :  62


cd [ffn_windows]/preprocessing/segment
python png_to_h5.py ground_truth.h5


cp [ffn_windows]/preprocessing/image/image.h5  [ffn_windows]/preprocessed_files/
cp [ffn_windows]/preprocessing/segment/ground_truth.h5  [ffn_windows]/preprocessed_files/


python  compute_partitions.py ^
    --input_volume  preprocessed_files/ground_truth.h5@raw ^
    --output_volume  preprocessed_files/af.h5@af ^
    --thresholds  0.025,0.05,0.075,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9 ^
    --lom_radius  24,24,24 ^
    --min_size  10000


Python  build_coordinates.py ^
     --partition_volumes	  validation1@preprocessed_files/af.h5@af ^
     --coordinate_output	  preprocessed_files/tf_record_file ^
     --margin 24,24,24


mkdir training_results
python train.py ^
    --train_coords  preprocessed_files/tf_record_file ^
    --data_volumes  validation1@[image]/image.h5@raw ^
    --label_volumes  validation1@[segment]/ground_truth.h5@raw ^
    --model_name  convstack_3d.ConvStack3DFFNModel ^
    --model_args  "{\"depth\":12,\"fov_size\":[33,33,33],\"deltas\":[8,8,8]}" ^
    --image_mean  131 ^
    --image_stddev  62 ^
    --train_dir  training_results ^
    --max_steps  1000000




build_coordinates.py
compute_partitions.py
train.py

split(':') => split('@')
2019/1/28 H Urakubo

storage.py , L58 
settings.hdf5.split(':') => split('@')
2019/1/29 H Urakubo


