from __future__ import annotations
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm

# Training Loop
def train_model(model, train_loader, val_loader, num_epochs, device, save_path='model.pth'):
    criterion = nn.CrossEntropyLoss()  # 255 is void class in Cityscapes
    optimizer = optim.AdamW(model.parameters(), lr=3e-4)

    best_val_loss = float('inf')

    for epoch in range(num_epochs):
        # Training Phase
        model.train()
        train_loss = 0.0
        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs} - Training")
        for images, labels in pbar:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * images.size(0)
            pbar.set_postfix({'Train Loss': loss.item()})

        train_loss /= len(train_loader.dataset)

        # Validation Phase
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for images, labels in tqdm(val_loader, desc=f"Epoch {epoch+1}/{num_epochs} - Validation"):
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * images.size(0)

                pbar.set_postfix({'Val Loss': loss.item()})

        val_loss /= len(val_loader.dataset)

        print(f"Epoch {epoch+1}/{num_epochs}")
        print(f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")

        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), save_path)
            print(f"Model saved at {save_path} with Val Loss: {val_loss:.4f}")

    return model