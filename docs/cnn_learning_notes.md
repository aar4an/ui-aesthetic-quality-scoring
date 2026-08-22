# CNN Learning Notes

## 1. What CNN is Doing
CNN (Convolutional Neural Network) processes images in layers:
- Convolution layers detect patterns like edges, shapes, textures
- Pooling layers reduce image size while keeping important features
- Fully connected layers combine all features for final classification
- Softmax output gives probability for each class (Good/Average/Poor)
In our model, 3 convolution layers extract visual features from
224x224 webpage screenshots before classifying them.

## 2. Why the Model May Overfit
Our model achieved 97.5% training accuracy but only 10% test
accuracy — a classic overfitting case. Reasons:
- Dataset is too small (only 50 images, 40 for training)
- Model has 12.8 million parameters but only 40 training samples
- Model memorizes training images instead of learning patterns
- No data augmentation was used to artificially increase data

## 3. Why More Data is Needed
CNNs need thousands of images to learn generalizable patterns.
With only 50 images:
- Model sees each image very few times
- Cannot learn what "Good UI" looks like in general
- Any noise in labels has huge impact
- Train/test split leaves very few samples for evaluation
Ideally 500-1000+ images per class would be needed for
a CNN trained from scratch to generalize well.

## 4. Why Transfer Learning is Useful
Transfer learning uses a model pre-trained on millions of images
(like ResNet trained on ImageNet with 1.2 million images).
Benefits:
- Already knows edges, shapes, textures from pre-training
- Only last few layers need to be fine-tuned on our data
- Works well even with small datasets like ours (50 images)
- Much faster training compared to training from scratch
- Higher accuracy with less data.