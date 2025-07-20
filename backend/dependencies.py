async def get_current_user():
    return None  # По умолчанию пользователь не авторизован

    # Альтернативный вариант с тестовым пользователем:
    # return {
    #     "username": "testuser",
    #     "full_name": "Test User",
    #     "email": "testuser@example.com"
    # }