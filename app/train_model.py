import torch
import torch.nn.functional as F
from app.model_architecture import HierarchicalDynamicGAT
from app.model import create_graph_from_api

model = HierarchicalDynamicGAT(in_dim=16, hidden_dim=32, out_dim=16, heads=4)
optimizer = torch.optim.Adam(model.parameters(), lr=0.005)

def train_model(model, drug_list, epochs=100):
    for epoch in range(epochs):
        losses = []
        for drug in drug_list:
            graph = create_graph_from_api(drug)
            if graph is None or graph.x.shape[0] == 0:
                continue

            model.train()
            optimizer.zero_grad()
            logits = model(graph.x, graph.edge_index)
            target = torch.ones(logits.shape)
            loss = F.mse_loss(logits, target)
            loss.backward()
            optimizer.step()
            losses.append(loss.item())

        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch + 1}, Avg Loss: {sum(losses) / len(losses)}")

    torch.save(model.state_dict(), "model_weights.pth")
    print("Model trained and saved as model_weights.pth")

if __name__ == "__main__":
    drugs = ["Aspirin", "Ibuprofen", "Paracetamol"]
    train_model(model, drugs)
