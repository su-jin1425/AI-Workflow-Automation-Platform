ROLE_ADMIN = "Admin"
ROLE_MANAGER = "Manager"
ROLE_OPERATOR = "Operator"
ROLE_VIEWER = "Viewer"

ROLE_PERMISSIONS = {
    ROLE_ADMIN: {
        "workflow:create",
        "workflow:update",
        "workflow:delete",
        "workflow:view",
        "workflow:rollback",
        "execution:start",
        "execution:cancel",
        "execution:view",
    },
    ROLE_MANAGER: {
        "workflow:create",
        "workflow:update",
        "workflow:view",
        "workflow:rollback",
        "execution:start",
        "execution:cancel",
        "execution:view",
    },
    ROLE_OPERATOR: {
        "workflow:view",
        "execution:start",
        "execution:view",
    },
    ROLE_VIEWER: {
        "workflow:view",
        "execution:view",
    },
}