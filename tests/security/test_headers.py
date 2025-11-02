def test_csp_header_is_restrictive_on_login(client):
    # Why: A restrictive CSP (default-src/script-src 'self') reduces XSS risk.
    resp = client.get("/auth/login")
    csp = resp.headers.get("Content-Security-Policy", "")
    assert "default-src 'self'" in csp
    assert "script-src 'self'" in csp
