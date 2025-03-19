import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATConv

# Dynamic Graph Attention Layer
class DynamicGraphAttentionLayer(nn.Module):
    def __init__(self, in_dim, out_dim, heads):
        super(DynamicGraphAttentionLayer, self).__init__()
        self.gat = GATConv(in_dim, out_dim, heads=heads)

    def forward(self, x, edge_index):
        return self.gat(x, edge_index)

# Hierarchical and Dynamic Graph Attention Model
class HierarchicalDynamicGAT(nn.Module):
    def __init__(self, in_dim, hidden_dim, out_dim, heads):
        super(HierarchicalDynamicGAT, self).__init__()
        self.gat1 = DynamicGraphAttentionLayer(in_dim, hidden_dim, heads)
        self.gat2 = DynamicGraphAttentionLayer(hidden_dim * heads, out_dim, 1)
        self.fc = nn.Linear(out_dim, 1)

    def forward(self, x, edge_index):
        h = self.gat1(x, edge_index)
        h = F.elu(h)
        h = self.gat2(h, edge_index)
        return self.fc(h).squeeze()