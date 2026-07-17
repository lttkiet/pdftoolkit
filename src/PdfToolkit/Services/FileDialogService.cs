using Avalonia.Controls;
using Avalonia.Platform.Storage;

namespace PdfToolkit.Services;

public interface IFileDialogService
{
    Task<string?> OpenPdfAsync(Window parent);
    Task<IReadOnlyList<string>> OpenMultiPdfAsync(Window parent);
    Task<string?> SavePdfAsync(Window parent, string defaultName);
    Task<string?> OpenImageAsync(Window parent);
    Task<IReadOnlyList<string>> OpenMultiImageAsync(Window parent);
    Task<string?> SaveImageAsync(Window parent, string defaultName);
    Task<string?> SaveTextAsync(Window parent, string defaultName);
}

public class FileDialogService : IFileDialogService
{
    public async Task<string?> OpenPdfAsync(Window parent)
    {
        var files = await parent.StorageProvider.OpenFilePickerAsync(new FilePickerOpenOptions
        {
            Title = "Open PDF",
            AllowMultiple = false,
            FileTypeFilter = [new FilePickerFileType("PDF Files") { Patterns = ["*.pdf"] }]
        });
        return files.Count > 0 ? files[0].TryGetLocalPath() : null;
    }

    public async Task<IReadOnlyList<string>> OpenMultiPdfAsync(Window parent)
    {
        var files = await parent.StorageProvider.OpenFilePickerAsync(new FilePickerOpenOptions
        {
            Title = "Open PDFs",
            AllowMultiple = true,
            FileTypeFilter = [new FilePickerFileType("PDF Files") { Patterns = ["*.pdf"] }]
        });
        return files.Select(f => f.TryGetLocalPath()).Where(p => p != null).Select(p => p!).ToList();
    }

    public async Task<string?> SavePdfAsync(Window parent, string defaultName)
    {
        var file = await parent.StorageProvider.SaveFilePickerAsync(new FilePickerSaveOptions
        {
            Title = "Save PDF",
            SuggestedFileName = defaultName,
            FileTypeChoices = [new FilePickerFileType("PDF Files") { Patterns = ["*.pdf"] }]
        });
        return file?.TryGetLocalPath();
    }

    public async Task<string?> OpenImageAsync(Window parent)
    {
        var files = await parent.StorageProvider.OpenFilePickerAsync(new FilePickerOpenOptions
        {
            Title = "Open Image",
            AllowMultiple = false,
            FileTypeFilter = [new FilePickerFileType("Image Files") { Patterns = ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif", "*.tiff"] }]
        });
        return files.Count > 0 ? files[0].TryGetLocalPath() : null;
    }

    public async Task<IReadOnlyList<string>> OpenMultiImageAsync(Window parent)
    {
        var files = await parent.StorageProvider.OpenFilePickerAsync(new FilePickerOpenOptions
        {
            Title = "Open Images",
            AllowMultiple = true,
            FileTypeFilter = [new FilePickerFileType("Image Files") { Patterns = ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif", "*.tiff"] }]
        });
        return files.Select(f => f.TryGetLocalPath()).Where(p => p != null).Select(p => p!).ToList();
    }

    public async Task<string?> SaveImageAsync(Window parent, string defaultName)
    {
        var file = await parent.StorageProvider.SaveFilePickerAsync(new FilePickerSaveOptions
        {
            Title = "Save Image",
            SuggestedFileName = defaultName,
            FileTypeChoices = [new FilePickerFileType("PNG Files") { Patterns = ["*.png"] }, new FilePickerFileType("JPEG Files") { Patterns = ["*.jpg", "*.jpeg"] }]
        });
        return file?.TryGetLocalPath();
    }

    public async Task<string?> SaveTextAsync(Window parent, string defaultName)
    {
        var file = await parent.StorageProvider.SaveFilePickerAsync(new FilePickerSaveOptions
        {
            Title = "Save Text",
            SuggestedFileName = defaultName,
            FileTypeChoices = [new FilePickerFileType("Text Files") { Patterns = ["*.txt"] }]
        });
        return file?.TryGetLocalPath();
    }
}
