let db = require('.');

class Subscription {
    constructor(subscriber_id, publisher_id) {
        this.subscriber_id = subscriber_id,
        this.publisher_id = publisher_id
    }

    static create(user_id, sub_id) {  
        let subscription = new Promise((resolve, reject) => {
            db.connection.query('INSERT INTO subscriptions SET ?', [user_id, sub_id], function(err, results) {
                if (err) reject(err);
                else resolve(results);
            });
        });
        return subscription;
    }

    // move to reading
    static findSubReadings(sub_id) {
        let subscriptionReadings = new Promise((resolve, reject) => {
            db.connection.query('SELECT readings.id, title, domain, description, readings.image as readings_image, word_count, url, readings.created_at, username, users.image, readings.user_id, favorites.user_id as favorite FROM subscriptions INNER JOIN readings ON publisher_id = readings.user_id LEFT JOIN favorites on favorites.reading_id = readings.id INNER JOIN users ON readings.user_id = users.id WHERE subscriber_id = ? ORDER BY readings.id DESC', sub_id, function(err, results) {
                if (err) reject(err);
                else resolve(results);
            });
        });
        return subscriptionReadings;
    }

    // don't need anymore
    static findSubWebsites(sub_id) {
        let subscriptionReadings = new Promise((resolve, reject) => {
            db.connection.query('SELECT domain FROM subscriptions INNER JOIN readings ON publisher_id = readings.user_id INNER JOIN users ON readings.user_id = users.id WHERE subscriber_id = ? GROUP BY domain ORDER BY COUNT(domain) DESC', sub_id, function(err, results) {
                if (err) reject(err);
                else resolve(results);
            });
        });
        return subscriptionReadings;
    }

    static findBySubId(sub_id) {
        let subscription = new Promise((resolve, reject) => {
            db.connection.query('SELECT * FROM subscriptions WHERE subscriber_id = ?', sub_id, function(err, results) {
                if (err) reject(err);
                else resolve(results);
            });
        });
        return subscription;
    }

    static delete(user_id, sub_id) {
        let subscription = new Promise((resolve, reject) => {
            db.connection.query('DELETE FROM subscriptions WHERE subscriber_id = ? AND publisher_id = ?', [user_id, sub_id], function(err, results) {
                if (err) reject(err);
                else resolve(results);
            });
        });
        return subscription;
    }
}

module.exports = Subscription;