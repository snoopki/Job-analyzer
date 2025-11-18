import { NavLink, Stack } from '@mantine/core';
import { Link, useLocation } from 'react-router-dom';

function Navbar({ onClose }) {
  const location = useLocation();

  const handleClick = () => {
    if (onClose) onClose();
  };

  return (
    <Stack gap="xs">
      <NavLink
        label="Analyze Page"
        component={Link}
        to="/"
        active={location.pathname === '/'}
        onClick={handleClick}
        variant="light"
      />
      <NavLink
        label="Dashboard"
        component={Link}
        to="/dashboard"
        active={location.pathname === '/dashboard'}
        onClick={handleClick}
        variant="light"
      />
    </Stack>
  );
}

export default Navbar;  