import torch
from .model_architecture import HierarchicalDynamicGAT  # Separate architecture file
from .api_handler import APIHandler  # Import API handling
from torch_geometric.data import Data

def load_model():
    """Loads the trained model from saved weights."""
    model = HierarchicalDynamicGAT(in_dim=16, hidden_dim=32, out_dim=16, heads=4)
    model.load_state_dict(torch.load("model_weights.pth"))
    model.eval()
    return model

def create_graph_from_api(drug_name):
    """Constructs a drug-disease graph from API data."""
    nodes = [drug_name]  # Drug as a node
    edges = []  # Placeholder for relationships

    # Fetch drug-disease data from APIs
    api_data = APIHandler.search_chembl(drug_name) 

    if "mechanisms" in api_data:
        for mech in api_data["mechanisms"]:
            disease = mech.get("disease_efficacy", "Unknown Disease")
            nodes.append(disease)
            edges.append((drug_name, disease))  # Drug -> Disease edge

    # Convert nodes to tensor features
    x = torch.randn((len(nodes), 16))  # Random feature vectors
    if edges:
        edge_index = torch.tensor([[nodes.index(src), nodes.index(dst)] for src, dst in edges], dtype=torch.long).T
    else:
        edge_index = torch.empty((2, 0), dtype=torch.long)  # Fix for empty edges
    return Data(x=x, edge_index=edge_index)

def predict_new_drug(drug_name):
    """Predicts disease associations for a drug using trained GAT model."""
    model = load_model()
    graph = create_graph_from_api(drug_name)

    if graph.x.shape[0] == 0:
        return f"No data found for {drug_name}."

    with torch.no_grad():
        logits = model(graph.x, graph.edge_index)

    return f"Predicted Disease for {drug_name}: {logits.mean().item()}"
