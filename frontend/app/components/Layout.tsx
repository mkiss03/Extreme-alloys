// frontend/app/components/Layout.tsx
import React from 'react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <span className="text-2xl font-bold text-blue-600">
                Extreme Alloys
              </span>
            </div>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-700 hover:text-blue-600 px-3 py-2">
                Dashboard
              </a>
              <a href="#" className="text-gray-700 hover:text-blue-600 px-3 py-2">
                History
              </a>
              <a href="#" className="text-gray-700 hover:text-blue-600 px-3 py-2">
                About
              </a>
            </div>
          </div>
        </div>
      </nav>

      <main>{children}</main>

      <footer className="bg-white mt-12 py-8 border-t">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-600">
          <p>&copy; 2025 Extreme Alloys. AI-powered materials science.</p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
