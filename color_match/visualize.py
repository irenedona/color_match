import os
import sys
from torch.utils.tensorboard import SummaryWriter
import numpy as np


class EmbeddingVisualiser:
    """Visualize an embedding in tensorboard
    """
    def __init__(self, df, label_cols, feat_cols, session_name=""):
        self.session_name = session_name
        self.labels = df[label_cols]
        self.features = df[feat_cols]
        self.writer = SummaryWriter(log_dir = os.path.join('.', 
                                                           'embedding',
                                                           self.session_name))


    def visualize(self, embeddings_folder):
        self.writer.add_embedding(self.features.values, 
                                  metadata=self.labels["colors"].values,
                                  tag="colors")

        self.writer.add_embedding(self.features.values, 
                                  metadata=self.labels["is_reference"].values,
                                  tag="Munsell points highlight")

