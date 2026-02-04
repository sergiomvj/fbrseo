import React, { useState, useEffect } from 'react';
import { apiService } from './services/api';
import './App.css';

// Simple inline styles to avoid needing too many files for now
const styles = {
    container: { maxWidth: '800px', margin: '0 auto', padding: '20px', fontFamily: 'system-ui, sans-serif' },
    card: { padding: '20px', border: '1px solid #ddd', borderRadius: '8px', marginBottom: '20px', backgroundColor: '#fff' },
    input: { padding: '10px', width: '100%', marginBottom: '10px', boxSizing: 'border-box' },
    button: { padding: '10px 20px', backgroundColor: '#0070f3', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' },
    statusOk: { color: 'green', fontWeight: 'bold' },
    statusError: { color: 'red', fontWeight: 'bold' },
    table: { width: '100%', borderCollapse: 'collapse' },
    th: { textAlign: 'left', padding: '10px', borderBottom: '1px solid #ddd' },
    td: { padding: '10px', borderBottom: '1px solid #ddd' }
};

function App() {
    const [apiKey, setApiKey] = useState(localStorage.getItem('seo_api_key') || '');
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [clientInfo, setClientInfo] = useState(null);
    const [domains, setDomains] = useState([]);
    const [health, setHealth] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // Check system health on load
    useEffect(() => {
        apiService.checkHealth()
            .then(() => setHealth('Online'))
            .catch(() => setHealth('Offline / Error'));

        if (apiKey) {
            handleVerify();
        }
    }, []);

    const handleVerify = async () => {
        setLoading(true);
        setError('');
        try {
            localStorage.setItem('seo_api_key', apiKey);
            const output = await apiService.verifyAuth();
            setClientInfo(output.data);
            setIsAuthenticated(true);

            // Fetch domains
            const domainsRes = await apiService.getDomains();
            setDomains(domainsRes.data);
        } catch (err) {
            console.error(err);
            setIsAuthenticated(false);
            localStorage.removeItem('seo_api_key');
            setError('Invalid API Key or server error');
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('seo_api_key');
        setApiKey('');
        setIsAuthenticated(false);
        setClientInfo(null);
    };

    return (
        <div style={styles.container}>
            <h1>🚀 SEO API Dashboard</h1>

            <div style={styles.card}>
                <h3>System Status: <span style={health === 'Online' ? styles.statusOk : styles.statusError}>{health || 'Checking...'}</span></h3>
            </div>

            {!isAuthenticated ? (
                <div style={styles.card}>
                    <h2>🔐 Login with API Key</h2>
                    <p>Please enter your SEO API Key to access the dashboard.</p>
                    <input
                        type="text"
                        placeholder="sk_live_..."
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        style={styles.input}
                    />
                    <button onClick={handleVerify} disabled={loading} style={styles.button}>
                        {loading ? 'Verifying...' : 'Access Dashboard'}
                    </button>
                    {error && <p style={{ color: 'red' }}>{error}</p>}
                </div>
            ) : (
                <>
                    <div style={styles.card}>
                        <h2>👤 Client Info</h2>
                        {clientInfo && (
                            <div>
                                <p><strong>Name:</strong> {clientInfo.name}</p>
                                <p><strong>Company:</strong> {clientInfo.company}</p>
                                <p><strong>Rate Limit:</strong> {clientInfo.rate_limits?.remaining_minute} / {clientInfo.rate_limits?.limit_minute} (min)</p>
                                <button onClick={handleLogout} style={{ ...styles.button, backgroundColor: '#666' }}>Logout</button>
                            </div>
                        )}
                    </div>

                    <div style={styles.card}>
                        <h2>🌐 Your Domains</h2>
                        {domains.length === 0 ? (
                            <p>No domains found. Create one via API!</p>
                        ) : (
                            <table style={styles.table}>
                                <thead>
                                    <tr>
                                        <th style={styles.th}>ID</th>
                                        <th style={styles.th}>Name</th>
                                        <th style={styles.th}>URL</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {domains.map(d => (
                                        <tr key={d.id}>
                                            <td style={styles.td}>{d.id}</td>
                                            <td style={styles.td}>{d.name}</td>
                                            <td style={styles.td}>{d.url}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                    </div>
                </>
            )}
        </div>
    );
}

export default App;
