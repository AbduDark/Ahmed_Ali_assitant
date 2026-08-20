import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import { Header } from './Header';

export default function DashboardLayout() {
  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="main-content-wrapper">
        <Header />
        <main className="page-container animate-page">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
