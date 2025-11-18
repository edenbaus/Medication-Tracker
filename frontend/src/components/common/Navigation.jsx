import { Link, useNavigate, useLocation } from 'react-router-dom';
import './Navigation.css';

function Navigation() {
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        navigate('/login');
    };

    return (
        <nav className="navigation">
            <div className="nav-container">
                <div className="nav-brand">
                    <h1>Medication Tracker</h1>
                </div>
                <div className="nav-links">
                    <Link
                        to="/"
                        className={location.pathname === '/' ? 'nav-link active' : 'nav-link'}
                    >
                        Medications
                    </Link>
                    <Link
                        to="/regimens"
                        className={location.pathname === '/regimens' ? 'nav-link active' : 'nav-link'}
                    >
                        Regimens
                    </Link>
                    <Link
                        to="/logs"
                        className={location.pathname === '/logs' ? 'nav-link active' : 'nav-link'}
                    >
                        Logs
                    </Link>
                    <Link
                        to="/tracking"
                        className={location.pathname === '/tracking' ? 'nav-link active' : 'nav-link'}
                    >
                        Tracking & Analytics
                    </Link>
                    <Link
                        to="/third-parties"
                        className={location.pathname === '/third-parties' ? 'nav-link active' : 'nav-link'}
                    >
                        Family & Others
                    </Link>
                    <button onClick={handleLogout} className="btn-logout">
                        Logout
                    </button>
                </div>
            </div>
        </nav>
    );
}

export default Navigation;
