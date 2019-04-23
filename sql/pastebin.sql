use pastebin;

CREATE TABLE IF NOT EXISTS paste (
    id BIGINT NOT NULL AUTO_INCREMENT,
    token VARCHAR(10) NOT NULL,
    user_id BIGINT,
    public BOOLEAN NOT NULL,
    document LONGTEXT NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    deleted_at DATETIME,
    PRIMARY KEY (id),
    UNIQUE KEY (token)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4;

CREATE TABLE IF NOT EXISTS user (
    id BIGINT NOT NULL AUTO_INCREMENT,
    account_id VARCHAR(128) NOT NULL,
    password VARBINARY(191) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    deleted_at DATETIME,
    PRIMARY KEY (id),
    UNIQUE KEY (account_id)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4;
