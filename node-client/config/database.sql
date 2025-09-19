-- Schema de base de données pour OpenRed Node Client
-- Ce fichier initialise la structure de données locale pour chaque node

-- Configuration et métadonnées du node
CREATE TABLE IF NOT EXISTS node_config (
    id INTEGER PRIMARY KEY,
    node_id VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    bio TEXT,
    avatar_url VARCHAR(255),
    server_url VARCHAR(255) NOT NULL,
    private_key_path VARCHAR(255),
    public_key_path VARCHAR(255),
    central_api_url VARCHAR(255) DEFAULT 'https://api.openred.org',
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Profil utilisateur étendu
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY,
    node_id VARCHAR(255) NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    birth_date DATE,
    location VARCHAR(255),
    website VARCHAR(255),
    occupation VARCHAR(255),
    interests TEXT, -- JSON array
    privacy_settings TEXT, -- JSON object
    theme_preferences TEXT, -- JSON object
    language VARCHAR(10) DEFAULT 'fr',
    timezone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (node_id) REFERENCES node_config(node_id)
);

-- Publications/Posts
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY,
    post_id VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    content_type VARCHAR(50) DEFAULT 'text', -- text, image, video, link
    media_urls TEXT, -- JSON array of media URLs
    visibility VARCHAR(50) DEFAULT 'public', -- public, friends, private, custom
    visibility_list TEXT, -- JSON array for custom visibility
    tags TEXT, -- JSON array of hashtags
    location VARCHAR(255),
    is_pinned BOOLEAN DEFAULT FALSE,
    reply_to_post_id VARCHAR(255), -- For threaded conversations
    share_original_post_id VARCHAR(255), -- For shares/reposts
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reply_to_post_id) REFERENCES posts(post_id),
    FOREIGN KEY (share_original_post_id) REFERENCES posts(post_id)
);

-- Réactions aux posts (likes, etc.)
CREATE TABLE IF NOT EXISTS post_reactions (
    id INTEGER PRIMARY KEY,
    post_id VARCHAR(255) NOT NULL,
    reactor_node_id VARCHAR(255) NOT NULL,
    reactor_username VARCHAR(255) NOT NULL,
    reaction_type VARCHAR(50) NOT NULL, -- like, love, laugh, angry, sad
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, reactor_node_id, reaction_type),
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE
);

-- Commentaires
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY,
    comment_id VARCHAR(255) UNIQUE NOT NULL,
    post_id VARCHAR(255) NOT NULL,
    parent_comment_id VARCHAR(255), -- For nested comments
    commenter_node_id VARCHAR(255) NOT NULL,
    commenter_username VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_comment_id) REFERENCES comments(comment_id) ON DELETE CASCADE
);

-- Connexions/Relations avec d'autres nodes
CREATE TABLE IF NOT EXISTS connections (
    id INTEGER PRIMARY KEY,
    connection_id VARCHAR(255) UNIQUE NOT NULL,
    target_node_id VARCHAR(255) NOT NULL,
    target_username VARCHAR(255) NOT NULL,
    target_display_name VARCHAR(255),
    target_server_url VARCHAR(255) NOT NULL,
    relationship_type VARCHAR(50) NOT NULL, -- friend, follower, following, blocked
    status VARCHAR(50) DEFAULT 'pending', -- pending, accepted, rejected, blocked
    initiated_by_me BOOLEAN NOT NULL, -- TRUE if I initiated the connection
    connection_date TIMESTAMP,
    notes TEXT, -- Private notes about this connection
    notification_settings TEXT, -- JSON object for notification preferences
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages privés
CREATE TABLE IF NOT EXISTS private_messages (
    id INTEGER PRIMARY KEY,
    message_id VARCHAR(255) UNIQUE NOT NULL,
    conversation_id VARCHAR(255) NOT NULL,
    sender_node_id VARCHAR(255) NOT NULL,
    sender_username VARCHAR(255) NOT NULL,
    recipient_node_id VARCHAR(255) NOT NULL,
    recipient_username VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    content_type VARCHAR(50) DEFAULT 'text', -- text, image, file
    media_url VARCHAR(255),
    is_read BOOLEAN DEFAULT FALSE,
    is_encrypted BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP
);

-- Conversations groupées
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY,
    conversation_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255), -- For group conversations
    type VARCHAR(50) NOT NULL, -- direct, group
    participants TEXT NOT NULL, -- JSON array of participant node_ids
    created_by_node_id VARCHAR(255) NOT NULL,
    last_message_id VARCHAR(255),
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (last_message_id) REFERENCES private_messages(message_id)
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY,
    notification_id VARCHAR(255) UNIQUE NOT NULL,
    type VARCHAR(100) NOT NULL, -- friend_request, post_like, comment, mention
    title VARCHAR(255) NOT NULL,
    content TEXT,
    source_node_id VARCHAR(255), -- Who generated this notification
    source_username VARCHAR(255),
    related_post_id VARCHAR(255), -- If related to a post
    related_comment_id VARCHAR(255), -- If related to a comment
    action_url VARCHAR(255), -- URL to navigate when clicked
    is_read BOOLEAN DEFAULT FALSE,
    priority VARCHAR(50) DEFAULT 'normal', -- low, normal, high, urgent
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    FOREIGN KEY (related_post_id) REFERENCES posts(post_id),
    FOREIGN KEY (related_comment_id) REFERENCES comments(comment_id)
);

-- Groupes/Communautés
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY,
    group_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    privacy VARCHAR(50) DEFAULT 'public', -- public, private, secret
    join_approval VARCHAR(50) DEFAULT 'open', -- open, approval_required, invite_only
    cover_image_url VARCHAR(255),
    rules TEXT,
    admin_node_ids TEXT, -- JSON array
    moderator_node_ids TEXT, -- JSON array
    member_count INTEGER DEFAULT 0,
    post_count INTEGER DEFAULT 0,
    created_by_node_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Adhésions aux groupes
CREATE TABLE IF NOT EXISTS group_memberships (
    id INTEGER PRIMARY KEY,
    group_id VARCHAR(255) NOT NULL,
    member_node_id VARCHAR(255) NOT NULL,
    member_username VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'member', -- member, moderator, admin
    status VARCHAR(50) DEFAULT 'active', -- active, pending, banned
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(group_id, member_node_id),
    FOREIGN KEY (group_id) REFERENCES groups(group_id) ON DELETE CASCADE
);

-- Cache des données externes (pour optimisation)
CREATE TABLE IF NOT EXISTS external_cache (
    id INTEGER PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    cache_type VARCHAR(100) NOT NULL, -- profile, post, node_status
    source_node_id VARCHAR(255),
    data TEXT NOT NULL, -- JSON data
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Journal d'activité local
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY,
    activity_type VARCHAR(100) NOT NULL,
    description TEXT,
    details TEXT, -- JSON object with additional data
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Paramètres et préférences
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY,
    setting_key VARCHAR(255) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(50) NOT NULL, -- string, number, boolean, json
    category VARCHAR(100), -- privacy, notifications, appearance
    description TEXT,
    is_user_configurable BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour optimiser les performances
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_visibility ON posts(visibility);
CREATE INDEX IF NOT EXISTS idx_connections_target_node ON connections(target_node_id);
CREATE INDEX IF NOT EXISTS idx_connections_status ON connections(status);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON private_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON private_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_external_cache_expires ON external_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_external_cache_key ON external_cache(cache_key);

-- Insertion des paramètres par défaut
INSERT OR IGNORE INTO settings (setting_key, setting_value, setting_type, category, description) VALUES
('privacy.default_post_visibility', 'public', 'string', 'privacy', 'Visibilité par défaut des nouvelles publications'),
('privacy.allow_friend_requests', 'true', 'boolean', 'privacy', 'Autoriser les demandes d''amis'),
('privacy.show_online_status', 'true', 'boolean', 'privacy', 'Afficher le statut en ligne'),
('notifications.friend_requests', 'true', 'boolean', 'notifications', 'Notifications pour les demandes d''amis'),
('notifications.post_reactions', 'true', 'boolean', 'notifications', 'Notifications pour les réactions aux posts'),
('notifications.comments', 'true', 'boolean', 'notifications', 'Notifications pour les commentaires'),
('notifications.mentions', 'true', 'boolean', 'notifications', 'Notifications pour les mentions'),
('appearance.theme', 'light', 'string', 'appearance', 'Thème de l''interface (light/dark)'),
('appearance.language', 'fr', 'string', 'appearance', 'Langue de l''interface'),
('sync.auto_sync_interval', '300', 'number', 'sync', 'Intervalle de synchronisation automatique en secondes'),
('sync.max_cache_age', '3600', 'number', 'sync', 'Âge maximum du cache en secondes');

-- Vue pour obtenir les statistiques du node
CREATE VIEW IF NOT EXISTS node_statistics AS
SELECT 
    (SELECT COUNT(*) FROM posts) as total_posts,
    (SELECT COUNT(*) FROM connections WHERE status = 'accepted') as total_friends,
    (SELECT COUNT(*) FROM connections WHERE status = 'accepted' AND relationship_type = 'follower') as total_followers,
    (SELECT COUNT(*) FROM connections WHERE status = 'accepted' AND relationship_type = 'following') as total_following,
    (SELECT COUNT(*) FROM notifications WHERE is_read = 0) as unread_notifications,
    (SELECT COUNT(*) FROM private_messages WHERE is_read = 0) as unread_messages;