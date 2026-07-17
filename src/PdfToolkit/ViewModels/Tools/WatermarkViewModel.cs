using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using PdfSharp.Drawing;
using PdfSharp.Pdf;
using PdfSharp.Pdf.IO;
using PdfToolkit.Services;

namespace PdfToolkit.ViewModels.Tools;

public partial class WatermarkViewModel : ViewModelBase
{
    private readonly MainWindowViewModel _mainVm;

    [ObservableProperty]
    private string _watermarkType = "Text";

    [ObservableProperty]
    private string _textContent = "CONFIDENTIAL";

    [ObservableProperty]
    private double _fontSize = 50;

    [ObservableProperty]
    private double _opacity = 30;

    [ObservableProperty]
    private double _angle = -45;

    [ObservableProperty]
    private string _imagePath = string.Empty;

    [ObservableProperty]
    private double _imageWidth = 200;

    [ObservableProperty]
    private string _pageRange = string.Empty;

    public WatermarkViewModel(MainWindowViewModel mainVm)
    {
        _mainVm = mainVm;
    }

    public List<string> WatermarkTypes { get; } = ["Text", "Image"];

    private List<int> GetTargetPages(int totalPages)
    {
        if (string.IsNullOrWhiteSpace(PageRange))
        {
            return Enumerable.Range(0, totalPages).ToList();
        }
        return PageRangeParser.Parse(PageRange, totalPages);
    }

    [RelayCommand]
    private async Task ApplyTextAsync()
    {
        if (_mainVm.DocumentModel.Document == null || !_mainVm.DocumentModel.IsOpen)
        {
            _mainVm.StatusText = "No PDF open. Open a PDF first.";
            return;
        }

        if (string.IsNullOrWhiteSpace(TextContent))
        {
            _mainVm.StatusText = "Enter watermark text.";
            return;
        }

        var savePath = await _mainVm.FileDialogService.SavePdfAsync(GetWindow(), "watermarked.pdf");
        if (savePath == null) return;

        try
        {
            using var srcDoc = PdfReader.Open(_mainVm.DocumentModel.FilePath!, PdfDocumentOpenMode.Import);
            using var result = new PdfDocument();

            var indices = GetTargetPages(srcDoc.PageCount);
            foreach (var i in indices)
            {
                var page = result.AddPage(srcDoc.Pages[i]);
                using var gfx = XGraphics.FromPdfPage(page);
                var font = new XFont("Arial", FontSize);

                var centerX = page.Width.Point / 2;
                var centerY = page.Height.Point / 2;

                gfx.Save();
                var matrix = XMatrix.Identity;
                matrix.RotatePrepend(Angle);
                matrix.TranslatePrepend(centerX, centerY);
                gfx.MultiplyTransform(matrix);

                var alpha = (int)(Opacity / 100.0 * 255);
                var brush = new XSolidBrush(XColor.FromArgb(alpha, 180, 180, 180));
                var textSize = gfx.MeasureString(TextContent, font);
                gfx.DrawString(TextContent, font, brush, new XPoint(-textSize.Width / 2, textSize.Height / 2));
                gfx.Restore();
            }

            result.Save(savePath);
            _mainVm.StatusText = $"Applied text watermark to {indices.Count} page(s)";
        }
        catch (Exception ex)
        {
            _mainVm.StatusText = $"Apply watermark failed: {ex.Message}";
        }
    }

    [RelayCommand]
    private async Task ApplyImageAsync()
    {
        if (_mainVm.DocumentModel.Document == null || !_mainVm.DocumentModel.IsOpen)
        {
            _mainVm.StatusText = "No PDF open. Open a PDF first.";
            return;
        }

        if (string.IsNullOrWhiteSpace(ImagePath) || !File.Exists(ImagePath))
        {
            _mainVm.StatusText = "Select a valid image file.";
            return;
        }

        var savePath = await _mainVm.FileDialogService.SavePdfAsync(GetWindow(), "watermarked.pdf");
        if (savePath == null) return;

        try
        {
            using var srcDoc = PdfReader.Open(_mainVm.DocumentModel.FilePath!, PdfDocumentOpenMode.Import);
            using var result = new PdfDocument();

            var indices = GetTargetPages(srcDoc.PageCount);
            foreach (var i in indices)
            {
                var page = result.AddPage(srcDoc.Pages[i]);
                using var gfx = XGraphics.FromPdfPage(page);
                var image = XImage.FromFile(ImagePath);

                var centerX = page.Width.Point / 2;
                var centerY = page.Height.Point / 2;

                gfx.Save();
                var matrix = XMatrix.Identity;
                matrix.RotatePrepend(Angle);
                matrix.TranslatePrepend(centerX, centerY);
                gfx.MultiplyTransform(matrix);

                var imgHeight = image.PixelHeight * (ImageWidth / image.PixelWidth);
                gfx.DrawImage(image, new XRect(-ImageWidth / 2, -imgHeight / 2, ImageWidth, imgHeight));

                gfx.Restore();
            }

            result.Save(savePath);
            _mainVm.StatusText = $"Applied image watermark to {indices.Count} page(s)";
        }
        catch (Exception ex)
        {
            _mainVm.StatusText = $"Apply watermark failed: {ex.Message}";
        }
    }

    [RelayCommand]
    private async Task SelectImageAsync()
    {
        var path = await _mainVm.FileDialogService.OpenImageAsync(GetWindow());
        if (path != null)
        {
            ImagePath = path;
        }
    }
}
