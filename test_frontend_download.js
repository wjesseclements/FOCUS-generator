// Test script to verify download functionality
// Run this in the browser console on http://localhost:3000

// Test 1: Check if the download URL is accessible
async function testDownloadUrl() {
    const testUrl = 'http://localhost:8000/files/aws-focus-2025-06.csv';
    
    try {
        const response = await fetch(testUrl);
        console.log('Fetch response:', {
            status: response.status,
            headers: Object.fromEntries(response.headers.entries()),
            ok: response.ok
        });
        
        if (response.ok) {
            const blob = await response.blob();
            console.log('Blob size:', blob.size);
            console.log('Blob type:', blob.type);
        }
    } catch (error) {
        console.error('Fetch error:', error);
    }
}

// Test 2: Test direct download
function testDirectDownload() {
    const a = document.createElement('a');
    a.href = 'http://localhost:8000/files/aws-focus-2025-06.csv';
    a.download = 'test.csv';
    a.click();
    console.log('Direct download triggered');
}

// Test 3: Check if ResultCard download button exists
function checkResultCard() {
    const downloadLinks = document.querySelectorAll('a[download]');
    console.log('Found download links:', downloadLinks.length);
    downloadLinks.forEach((link, index) => {
        console.log(`Link ${index}:`, {
            href: link.href,
            download: link.download,
            className: link.className,
            text: link.textContent
        });
    });
}

console.log('Run these tests:');
console.log('1. testDownloadUrl() - Check if URL is accessible');
console.log('2. testDirectDownload() - Test direct download');
console.log('3. checkResultCard() - Check if download button exists after generation');