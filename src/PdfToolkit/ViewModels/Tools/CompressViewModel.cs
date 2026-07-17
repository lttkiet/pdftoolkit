using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using PdfSharp.Pdf;
using PdfSharp.Pdf.IO;

namespace PdfToolkit.ViewModels.Tools;

public partial class CompressViewModel : ViewModelBase
{
    private readonly MainWindowViewModel _mainVm;

    [ObservableProperty]
    private int _quality = 50;

    [ObservableProperty]
    private bool _removeUnusedObjects = true;

    [ObservableProperty]
    private string _resultText = string.Empty;

    public CompressViewModel(MainWindowViewModel mainVm)
    {
        _mainVm = mainVm;
    }

    [RelayCommand]
    private async Task CompressAsync()
    {
        string? sourcePath = null;

        if (_mainVm.DocumentModel.IsOpen)
        {
            sourcePath = _mainVm.DocumentModel.FilePath;
        }
        else
        {
            sourcePath = await _mainVm.FileDialogService.OpenPdfAsync(GetWindow());
        }

        if (sourcePath == null)
        {
            _mainVm.StatusText = "No PDF file selected";
            return;
        }

        var savePath = await _mainVm.FileDialogService.SavePdfAsync(GetWindow(), "compressed.pdf");
        if (savePath == null) return;

        try
        {
            var originalSize = new FileInfo(sourcePath).Length;

            using var doc = PdfReader.Open(sourcePath, PdfDocumentOpenMode.Import);
            doc.Options.CompressContentStreams = true;
            doc.Options.NoCompression = false;
            doc.Options.EnableCcittCompressionForBilevelImages = true;
            doc.Options.UseFlateDecoderForJpegImages = RemoveUnusedObjects
                ? PdfUseFlateDecoderForJpegImages.Automatic
                : PdfUseFlateDecoderForJpegImages.Never;
            doc.Save(savePath);

            var compressedSize = new FileInfo(savePath).Length;
            var savings = originalSize > 0 ? (1.0 - (double)compressedSize / originalSize) * 100 : 0;

            ResultText = $"Original: {FormatSize(originalSize)}\n" +
                         $"Compressed: {FormatSize(compressedSize)}\n" +
                         $"Savings: {savings:F1}%";

            _mainVm.StatusText = $"Compressed: {FormatSize(originalSize)} → {FormatSize(compressedSize)} ({savings:F1}% savings)";
        }
        catch (Exception ex)
        {
            _mainVm.StatusText = $"Compress failed: {ex.Message}";
        }
    }

    private static string FormatSize(long bytes)
    {
        if (bytes < 1024) return $"{bytes} B";
        if (bytes < 1024 * 1024) return $"{bytes / 1024.0:F1} KB";
        return $"{bytes / (1024.0 * 1024.0):F1} MB";
    }
}
