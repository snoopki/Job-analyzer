import { Container, LoadingOverlay, Box } from '@mantine/core';
import { useAnalyzeCV } from '../hooks/useAnalyzeCV';
import Loader from '../components/Loader';
import CVInputForm from '../components/CVInputForm';
import AnalysisResults from '../components/AnalysisResults';

function AnalyzePage() {
  const { results, isLoading, error, analyze } = useAnalyzeCV();

  const handleSubmit = (cvText) => {
    analyze(cvText);
  };

  return (
    <Container size="md" px="md" py="xl" style={{ direction: 'rtl', textAlign: 'right', minHeight: '80vh', position: 'relative', overflow: 'hidden' }}>
      
      <LoadingOverlay
        visible={isLoading}
        overlayProps={{ radius: 'sm', blur: 2 }}
        loaderProps={{ children: <Loader /> }}
        zIndex={1000}
        style={{ position: 'fixed', inset: 0 }}
      />

      <Box mb={30}>
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