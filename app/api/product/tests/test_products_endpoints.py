def test_create_product(fastapi_client):
    product_data = {
        "name": "Test Product",
        "description": "A product for testing",
        "price": 19.99,
        "inventory": 10,
    }
    response = fastapi_client.post("api/products/", json=product_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["description"] == product_data["description"]
    assert data["price"] == product_data["price"]
    assert data["inventory"] == product_data["inventory"]


def test_get_product(fastapi_client, product1):
    response = fastapi_client.get(f"api/products/{product1.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product1.id
    assert data["name"] == product1.name
    assert data["description"] == product1.description
    assert data["price"] == product1.price
    assert data["inventory"] == product1.inventory


def test_update_product_inventory(fastapi_client, product1):
    # increase the inventory by 5

    update_data = {"quantity": 5, "type": "add", "reason_code": "restock"}

    response = fastapi_client.put(
        f"api/products/{product1.id}/inventory", json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["inventory"] == product1.inventory + update_data["quantity"]

    # decrease the inventory by 3
    update_data = {"quantity": 3, "type": "remove", "reason_code": "sale"}

    response = fastapi_client.put(
        f"api/products/{product1.id}/inventory", json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["inventory"] == product1.inventory + 5 - update_data["quantity"]

    # try to decrease the inventory by more than available
    update_data = {"quantity": 200, "type": "remove", "reason_code": "error"}

    response = fastapi_client.put(
        f"api/products/{product1.id}/inventory", json=update_data
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Insufficient inventory to remove the requested quantity."
