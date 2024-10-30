import React from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import './NavigationBar.css';

function NavigationBar() {
  const location = useLocation();

  const hiddenRoutes = ['/login', '/register'];
  const isHiddenRoute = hiddenRoutes.includes(location.pathname);

  if (!isHiddenRoute) {
    return (
      <nav className="nav">
        <NavLink exact to="/" activeClassName="active" className="nav-link">
          <img src="/home-icon.jpg" alt="Home" />
          General
        </NavLink>
        <NavLink to="/algorithms" activeClassName="active" className="nav-link">
          <img src="/algorithm-icon.jpg" alt="Algorithms" />
          Algorithms
        </NavLink>
        <NavLink to="/manager" activeClassName="active" className="nav-link">
          <img src="/manager-icon.jpg" alt="Manager" />
          Crop Manager
        </NavLink>
      </nav>
    );
  }

  return null;
}

export default NavigationBar;