import { NavLink } from '@mantine/core';
import { Link, useLocation } from 'react-router-dom';
// חשוב לייבא גם את Link וגם את useLocation

function Navbar() {
  const location = useLocation();

  return (
    <>
      <NavLink
        label="Analyze Page"
        component={Link} 
        to="/"          
        active={location.pathname === '/'} 
      />
      <NavLink
        label="Dashboard"
        component={Link} 
        to="/dashboard"  
        active={location.pathname === '/dashboard'} 
      />
    </>
  );
}

export default Navbar;