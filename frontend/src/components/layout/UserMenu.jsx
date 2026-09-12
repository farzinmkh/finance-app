import { useNavigate } from "react-router-dom";
import { User, Settings, LogOut } from "lucide-react";
import { Dropdown } from "../ui/Dropdown";
import { Avatar } from "../ui/Avatar";
import { useAuth } from "../../hooks/useAuth";
import "./UserMenu.css";

export function UserMenu() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <Dropdown
      align="end"
      trigger={
        <button type="button" className="user-menu-trigger" aria-label="Open user menu">
          <Avatar name={user?.email} size="sm" />
        </button>
      }
    >
      <div className="user-menu__header">
        <p className="text-label user-menu__email">{user?.email || "Guest"}</p>
        <p className="text-caption">Personal workspace</p>
      </div>
      <Dropdown.Separator />
      <Dropdown.Item onClick={() => navigate("/profile")}>
        <User size={14} /> Profile
      </Dropdown.Item>
      <Dropdown.Item onClick={() => navigate("/settings")}>
        <Settings size={14} /> Settings
      </Dropdown.Item>
      <Dropdown.Separator />
      <Dropdown.Item tone="danger" onClick={() => { logout(); navigate("/login"); }}>
        <LogOut size={14} /> Log out
      </Dropdown.Item>
    </Dropdown>
  );
}
