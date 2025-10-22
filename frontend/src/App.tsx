import React, { useState } from 'react';
import {
  Container,
  AppBar,
  Toolbar,
  Typography,
  Box,
  CssBaseline,
} from '@mui/material';
import { motion } from 'framer-motion';
// import DashboardPage from './components/pages/DashboardPage';
// import AnalysisPage from './components/pages/AnalysisPage';
// import HistoryPage from './components/pages/HistoryPage';
// import Navigation from './components/layout/Navigation';
// import { AnalysisProvider } from './contexts/AnalysisContext';
import DashboardPage from './components/pages/DashboardPage';
import AnalysisPage from './components/pages/AnalysisPage';
import HistoryPage from './components/pages/HistoryPage';
import Navigation from './components/layout/Navigation';
import { AnalysisProvider } from './contexts/AnalysisContext';



function App() {
  const [currentPage, setCurrentPage] = useState<'dashboard' | 'analysis' | 'history'>('dashboard');

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <DashboardPage />;
      case 'analysis':
        return <AnalysisPage />;
      case 'history':
        return <HistoryPage />;
      default:
        return <DashboardPage />;
    }
  };

  return (
    <AnalysisProvider>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Reddit Sentiment Analysis
            </Typography>
          </Toolbar>
        </AppBar>
        
        <Box sx={{ display: 'flex', flex: 1 }}>
          <Navigation currentPage={currentPage} onPageChange={setCurrentPage} />
          
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 3,
              mt: 8, // Account for AppBar height
              backgroundColor: 'background.default',
            }}
          >
            <Container maxWidth="xl">
              <motion.div
                key={currentPage}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                {renderPage()}
              </motion.div>
            </Container>
          </Box>
        </Box>
      </Box>
    </AnalysisProvider>
  );
}

export default App;