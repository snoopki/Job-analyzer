import { Container, LoadingOverlay, Box } from '@mantine/core';
import { useMediaQuery } from '@mantine/hooks'; 
import { useAnalyzeCV } from '../hooks/useAnalyzeCV';
import Loader from '../components/Loader';
import CVInputForm from '../components/CVInputForm';
import AnalysisResults from '../components/AnalysisResults';

function AnalyzePage() {
  const { results, isLoading, error, analyze } = useAnalyzeCV();
  const isMobile = useMediaQuery('(max-width: 768px)'); 

  const handleSubmit = (cvText) => {
    analyze(cvText);
  };

  return (
    <Container 
      size="md" 
      px={isMobile ? 0 : "md"}
      py="xl" 
      style={{ direction: 'rtl', textAlign: 'right', minHeight: '80vh', position: 'relative', overflow: 'visible' }}
    >
      
      <LoadingOverlay
        visible={isLoading}
        overlayProps={{ radius: 'sm', blur: 2 }}
        loaderProps={{ children: <Loader /> }}
        zIndex={1000}
        style={{ position: 'fixed', inset: 0 }}
      />

      <Box mb={30} px={isMobile ? "xs" : 0}>
        <CVInputForm
          isLoading={isLoading}
          onSubmit={handleSubmit}
        />
      </Box>

      {results && !isLoading && !error && (
        <AnalysisResults results={results} />
      )}
    </Container>
  );
}

export default AnalyzePage;